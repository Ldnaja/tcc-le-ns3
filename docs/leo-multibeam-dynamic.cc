#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/point-to-point-net-device.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("LeoMultibeamDynamicV3");

struct BeamRuntimeState
{
    uint32_t beamId = 0;

    double offeredPayloadMbps = 0.0;
    double offeredIpMbps = 0.0;

    double virtualBacklogMb = 0.0;

    uint32_t allocatedChannels = 0;
    double beamCapacityMbps = 0.0;

    double estimatedServedMb = 0.0;
    double estimatedUtilization = 0.0;

    /*
     * EWMA of estimated service rate.
     * Used by proportional_fair to avoid repeatedly favoring only the same beam.
     */
    double ewmaServedMbps = 0.0;
};

struct BeamFlowMetrics
{
    uint64_t txPackets = 0;
    uint64_t rxPackets = 0;
    uint64_t lostPackets = 0;

    uint64_t txBytes = 0;
    uint64_t rxBytes = 0;

    double delaySumSeconds = 0.0;
    double firstTx = std::numeric_limits<double>::max();
    double lastRx = 0.0;
};

static double
JainFairness(const std::vector<double>& values)
{
    double sum = 0.0;
    double sumSquares = 0.0;
    uint32_t n = 0;

    for (double v : values)
    {
        if (v < 0.0)
        {
            continue;
        }

        sum += v;
        sumSquares += v * v;
        n++;
    }

    if (n == 0 || sumSquares == 0.0)
    {
        return 0.0;
    }

    return (sum * sum) / (static_cast<double>(n) * sumSquares);
}

static std::vector<uint32_t>
ActiveBeamIds(const std::vector<BeamRuntimeState>& beams)
{
    std::vector<uint32_t> active;

    for (const auto& beam : beams)
    {
        if (beam.offeredIpMbps > 0.0 || beam.virtualBacklogMb > 1e-9)
        {
            active.push_back(beam.beamId);
        }
    }

    return active;
}

static void
GiveMinimumChannels(std::vector<uint32_t>& alloc,
                    const std::vector<uint32_t>& active,
                    uint32_t& channelsLeft,
                    uint32_t minChannelsPerActiveBeam,
                    uint32_t maxChannelsPerBeam)
{
    if (active.empty() || channelsLeft == 0 || minChannelsPerActiveBeam == 0)
    {
        return;
    }

    uint32_t effectiveMin = std::min(minChannelsPerActiveBeam, maxChannelsPerBeam);

    for (uint32_t r = 0; r < effectiveMin; ++r)
    {
        for (uint32_t beamId : active)
        {
            if (channelsLeft == 0)
            {
                return;
            }

            if (alloc[beamId] < effectiveMin && alloc[beamId] < maxChannelsPerBeam)
            {
                alloc[beamId]++;
                channelsLeft--;
            }
        }
    }
}

static double
StepDemandMb(const BeamRuntimeState& beam, double controlInterval)
{
    return beam.offeredIpMbps * controlInterval / 8.0;
}

static double
ChannelCapacityMb(double channelCapacityMbps, double controlInterval)
{
    return channelCapacityMbps * controlInterval / 8.0;
}

static std::vector<double>
InitialResidualPressureMb(const std::vector<BeamRuntimeState>& beams,
                          double controlInterval)
{
    std::vector<double> residual(beams.size(), 0.0);

    for (const auto& beam : beams)
    {
        /*
         * Pressure = backlog already accumulated + current step demand.
         * This is intentionally IP-level to match NS-3 packet/link capacity.
         */
        residual[beam.beamId] = beam.virtualBacklogMb + StepDemandMb(beam, controlInterval);
    }

    return residual;
}

static void
SubtractAllocatedCapacityFromResidual(std::vector<double>& residual,
                                      const std::vector<uint32_t>& alloc,
                                      double channelCapacityMbps,
                                      double controlInterval)
{
    double channelMb = ChannelCapacityMb(channelCapacityMbps, controlInterval);

    for (uint32_t i = 0; i < residual.size(); ++i)
    {
        residual[i] = std::max(0.0, residual[i] - static_cast<double>(alloc[i]) * channelMb);
    }
}

static std::vector<uint32_t>
AllocateChannels(const std::string& policy,
                 const std::vector<BeamRuntimeState>& beams,
                 uint32_t totalChannels,
                 uint32_t maxChannelsPerBeam,
                 uint32_t minChannelsPerActiveBeam,
                 double channelCapacityMbps,
                 double controlInterval,
                 uint32_t stepIdx)
{
    std::vector<uint32_t> alloc(beams.size(), 0);
    std::vector<uint32_t> active = ActiveBeamIds(beams);

    if (active.empty() || totalChannels == 0 || maxChannelsPerBeam == 0)
    {
        return alloc;
    }

    uint32_t channelsLeft = totalChannels;

    /*
     * Starvation protection.
     * This avoids unrealistic NS-3 packet loss caused by completely closing
     * active beams while UDP applications continue generating traffic.
     */
    GiveMinimumChannels(alloc,
                        active,
                        channelsLeft,
                        minChannelsPerActiveBeam,
                        maxChannelsPerBeam);

    if (channelsLeft == 0)
    {
        return alloc;
    }

    double channelMb = ChannelCapacityMb(channelCapacityMbps, controlInterval);

    /*
     * Equal baseline:
     * Ignores backlog and demand. It simply spreads remaining channels.
     */
    if (policy == "equal")
    {
        while (channelsLeft > 0)
        {
            bool progress = false;

            for (uint32_t beamId : active)
            {
                if (alloc[beamId] < maxChannelsPerBeam)
                {
                    alloc[beamId]++;
                    channelsLeft--;
                    progress = true;

                    if (channelsLeft == 0)
                    {
                        break;
                    }
                }
            }

            if (!progress)
            {
                break;
            }
        }

        return alloc;
    }

    /*
     * Round-robin baseline:
     * Same as equal, but rotates the starting beam at each control step.
     */
    if (policy == "round_robin")
    {
        uint32_t shift = active.empty() ? 0 : stepIdx % active.size();
        std::rotate(active.begin(), active.begin() + shift, active.end());

        while (channelsLeft > 0)
        {
            bool progress = false;

            for (uint32_t beamId : active)
            {
                if (alloc[beamId] < maxChannelsPerBeam)
                {
                    alloc[beamId]++;
                    channelsLeft--;
                    progress = true;

                    if (channelsLeft == 0)
                    {
                        break;
                    }
                }
            }

            if (!progress)
            {
                break;
            }
        }

        return alloc;
    }

    /*
     * Longest Queue First:
     * Backlog-oriented, but moderate.
     * It assigns one channel at a time to the currently largest residual queue.
     * After assigning a channel, residual pressure is reduced. This avoids
     * blindly filling one beam to the maximum before serving others.
     */
    if (policy == "longest_queue_first")
    {
        std::vector<double> residual = InitialResidualPressureMb(beams, controlInterval);
        SubtractAllocatedCapacityFromResidual(residual, alloc, channelCapacityMbps, controlInterval);

        while (channelsLeft > 0)
        {
            int bestBeam = -1;
            double bestResidual = 1e-12;

            for (uint32_t beamId : active)
            {
                if (alloc[beamId] >= maxChannelsPerBeam)
                {
                    continue;
                }

                if (residual[beamId] > bestResidual)
                {
                    bestResidual = residual[beamId];
                    bestBeam = static_cast<int>(beamId);
                }
            }

            if (bestBeam < 0)
            {
                break;
            }

            alloc[bestBeam]++;
            channelsLeft--;

            residual[bestBeam] = std::max(0.0, residual[bestBeam] - channelMb);
        }

        return alloc;
    }

    /*
     * Greedy Backlog:
     * More aggressive than longest_queue_first.
     * It orders beams by residual pressure and satisfies the largest queues
     * up to maxChannelsPerBeam before moving to the next one.
     * It does NOT allocate useless extra channels once residual demand is covered.
     */
    if (policy == "greedy_backlog")
    {
        std::vector<double> residual = InitialResidualPressureMb(beams, controlInterval);
        SubtractAllocatedCapacityFromResidual(residual, alloc, channelCapacityMbps, controlInterval);

        std::sort(active.begin(), active.end(), [&residual](uint32_t a, uint32_t b) {
            if (std::abs(residual[a] - residual[b]) < 1e-12)
            {
                return a < b;
            }
            return residual[a] > residual[b];
        });

        for (uint32_t beamId : active)
        {
            while (channelsLeft > 0 &&
                   alloc[beamId] < maxChannelsPerBeam &&
                   residual[beamId] > 1e-12)
            {
                alloc[beamId]++;
                channelsLeft--;

                residual[beamId] = std::max(0.0, residual[beamId] - channelMb);
            }

            if (channelsLeft == 0)
            {
                break;
            }
        }

        return alloc;
    }

    /*
     * Proportional Fair approximation:
     * Uses residual pressure divided by a historical service estimate.
     * A beam with high backlog and low recent service receives higher priority.
     * This is intentionally more balanced than pure greedy allocation.
     */
    if (policy == "proportional_fair")
    {
        std::vector<double> residual = InitialResidualPressureMb(beams, controlInterval);
        SubtractAllocatedCapacityFromResidual(residual, alloc, channelCapacityMbps, controlInterval);

        while (channelsLeft > 0)
        {
            int bestBeam = -1;
            double bestScore = 1e-12;

            for (uint32_t beamId : active)
            {
                if (alloc[beamId] >= maxChannelsPerBeam)
                {
                    continue;
                }

                if (residual[beamId] <= 1e-12)
                {
                    continue;
                }

                double historicalService = std::max(0.10, beams[beamId].ewmaServedMbps);
                double allocationPenalty = 1.0 + static_cast<double>(alloc[beamId]);

                double score = residual[beamId] / (historicalService * allocationPenalty);

                if (score > bestScore)
                {
                    bestScore = score;
                    bestBeam = static_cast<int>(beamId);
                }
            }

            if (bestBeam < 0)
            {
                break;
            }

            alloc[bestBeam]++;
            channelsLeft--;

            residual[bestBeam] = std::max(0.0, residual[bestBeam] - channelMb);
        }

        return alloc;
    }

    NS_ABORT_MSG("Unknown policy: " << policy);
}

static void
ApplyLinkRates(const std::vector<BeamRuntimeState>& beams,
               const std::vector<Ptr<PointToPointNetDevice>>& satelliteDevices,
               const std::vector<Ptr<PointToPointNetDevice>>& sourceDevices)
{
    for (const auto& beam : beams)
    {
        double rateMbps = std::max(beam.beamCapacityMbps, 0.001);
        uint64_t rateBps = static_cast<uint64_t>(rateMbps * 1e6);

        DataRate rate(rateBps);

        satelliteDevices[beam.beamId]->SetDataRate(rate);
        sourceDevices[beam.beamId]->SetDataRate(rate);
    }
}

static void
ControlStep(std::vector<BeamRuntimeState>* beams,
            std::vector<Ptr<PointToPointNetDevice>>* satelliteDevices,
            std::vector<Ptr<PointToPointNetDevice>>* sourceDevices,
            std::ofstream* history,
            std::string policy,
            uint32_t totalChannels,
            uint32_t maxChannelsPerBeam,
            uint32_t minChannelsPerActiveBeam,
            double channelCapacityMbps,
            double controlInterval,
            double currentTime,
            double stopTime,
            uint32_t stepIdx)
{
    for (auto& beam : *beams)
    {
        double offeredMbThisStep = beam.offeredIpMbps * controlInterval / 8.0;

        beam.virtualBacklogMb += offeredMbThisStep;
        beam.estimatedServedMb = 0.0;
        beam.estimatedUtilization = 0.0;
    }

    std::vector<uint32_t> alloc =
        AllocateChannels(policy,
                         *beams,
                         totalChannels,
                         maxChannelsPerBeam,
                         minChannelsPerActiveBeam,
                         channelCapacityMbps,
                         controlInterval,
                         stepIdx);

    double ewmaAlpha = 0.20;

    for (auto& beam : *beams)
    {
        beam.allocatedChannels = alloc[beam.beamId];
        beam.beamCapacityMbps = static_cast<double>(beam.allocatedChannels) * channelCapacityMbps;

        double capacityMbThisStep = beam.beamCapacityMbps * controlInterval / 8.0;

        beam.estimatedServedMb = std::min(beam.virtualBacklogMb, capacityMbThisStep);
        beam.virtualBacklogMb -= beam.estimatedServedMb;

        if (capacityMbThisStep > 0.0)
        {
            beam.estimatedUtilization = beam.estimatedServedMb / capacityMbThisStep;
        }
        else
        {
            beam.estimatedUtilization = 0.0;
        }

        double servedMbps = beam.estimatedServedMb * 8.0 / controlInterval;

        if (beam.ewmaServedMbps <= 1e-12)
        {
            beam.ewmaServedMbps = servedMbps;
        }
        else
        {
            beam.ewmaServedMbps =
                (1.0 - ewmaAlpha) * beam.ewmaServedMbps + ewmaAlpha * servedMbps;
        }
    }

    ApplyLinkRates(*beams, *satelliteDevices, *sourceDevices);

    for (const auto& beam : *beams)
    {
        (*history) << std::fixed << std::setprecision(6)
                   << currentTime << ","
                   << beam.beamId << ","
                   << policy << ","
                   << beam.offeredPayloadMbps << ","
                   << beam.offeredIpMbps << ","
                   << beam.virtualBacklogMb << ","
                   << beam.allocatedChannels << ","
                   << beam.beamCapacityMbps << ","
                   << beam.estimatedServedMb << ","
                   << beam.estimatedUtilization << ","
                   << beam.ewmaServedMbps << "\n";
    }

    history->flush();

    double nextTime = currentTime + controlInterval;

    if (nextTime < stopTime - 1e-9)
    {
        Simulator::Schedule(Seconds(controlInterval),
                            &ControlStep,
                            beams,
                            satelliteDevices,
                            sourceDevices,
                            history,
                            policy,
                            totalChannels,
                            maxChannelsPerBeam,
                            minChannelsPerActiveBeam,
                            channelCapacityMbps,
                            controlInterval,
                            nextTime,
                            stopTime,
                            stepIdx + 1);
    }
}

int
main(int argc, char* argv[])
{
    uint32_t nBeams = 19;
    uint32_t nUsersPerBeam = 4;
    uint32_t hotspotBeam = 0;

    double simTime = 120.0;
    double appStartTime = 1.0;
    double drainTime = 5.0;
    double controlInterval = 1.0;

    double baseUserRateMbps = 0.50;
    double hotspotUserRateMbps = 2.00;

    uint32_t totalChannels = 48;
    uint32_t maxChannelsPerBeam = 6;
    uint32_t minChannelsPerActiveBeam = 1;

    double channelCapacityMbps = 1.1;
    double initialBeamLinkRateMbps = 1.0;
    double leoDelayMs = 20.0;

    uint32_t packetSize = 1000;
    std::string policy = "proportional_fair";

    CommandLine cmd(__FILE__);
    cmd.AddValue("nBeams", "Number of logical beams", nBeams);
    cmd.AddValue("nUsersPerBeam", "Number of represented users inside each aggregate beam flow", nUsersPerBeam);
    cmd.AddValue("hotspotBeam", "Beam receiving higher traffic load", hotspotBeam);
    cmd.AddValue("simTime", "Application traffic duration in seconds", simTime);
    cmd.AddValue("baseUserRateMbps", "Payload Mbps per represented user in normal beams", baseUserRateMbps);
    cmd.AddValue("hotspotUserRateMbps", "Payload Mbps per represented user in hotspot beam", hotspotUserRateMbps);
    cmd.AddValue("totalChannels", "Total number of channels available for allocation", totalChannels);
    cmd.AddValue("maxChannelsPerBeam", "Maximum number of channels per beam", maxChannelsPerBeam);
    cmd.AddValue("minChannelsPerActiveBeam", "Minimum number of channels for each active beam", minChannelsPerActiveBeam);
    cmd.AddValue("channelCapacityMbps", "Capacity represented by one allocated channel in Mbps", channelCapacityMbps);
    cmd.AddValue("policy", "Allocation policy: equal, round_robin, longest_queue_first, greedy_backlog, proportional_fair", policy);
    cmd.AddValue("controlInterval", "Dynamic allocation interval in seconds", controlInterval);
    cmd.AddValue("leoDelayMs", "One-way propagation delay of each beam link in ms", leoDelayMs);
    cmd.AddValue("packetSize", "UDP payload packet size in bytes", packetSize);
    cmd.Parse(argc, argv);

    if (hotspotBeam >= nBeams)
    {
        NS_ABORT_MSG("hotspotBeam must be smaller than nBeams");
    }

    if (minChannelsPerActiveBeam > maxChannelsPerBeam)
    {
        NS_ABORT_MSG("minChannelsPerActiveBeam must be <= maxChannelsPerBeam");
    }

    NodeContainer satellite;
    satellite.Create(1);

    NodeContainer beamSources;
    beamSources.Create(nBeams);

    InternetStackHelper internet;
    internet.Install(satellite);
    internet.Install(beamSources);

    std::map<uint32_t, uint32_t> addressToBeam;
    std::vector<Ipv4InterfaceContainer> p2pIfaces(nBeams);
    std::vector<Ptr<PointToPointNetDevice>> satelliteDevices(nBeams);
    std::vector<Ptr<PointToPointNetDevice>> sourceDevices(nBeams);

    for (uint32_t b = 0; b < nBeams; ++b)
    {
        PointToPointHelper p2p;
        p2p.SetDeviceAttribute("DataRate", StringValue(std::to_string(initialBeamLinkRateMbps) + "Mbps"));
        p2p.SetChannelAttribute("Delay", StringValue(std::to_string(leoDelayMs) + "ms"));
        p2p.SetQueue("ns3::DropTailQueue<Packet>", "MaxSize", StringValue("10000p"));

        NetDeviceContainer devices = p2p.Install(satellite.Get(0), beamSources.Get(b));

        satelliteDevices[b] = DynamicCast<PointToPointNetDevice>(devices.Get(0));
        sourceDevices[b] = DynamicCast<PointToPointNetDevice>(devices.Get(1));

        std::ostringstream subnet;
        subnet << "10." << (b + 1) << ".0.0";

        Ipv4AddressHelper address;
        address.SetBase(subnet.str().c_str(), "255.255.255.0");
        p2pIfaces[b] = address.Assign(devices);

        Ipv4Address beamSourceAddress = p2pIfaces[b].GetAddress(1);
        addressToBeam[beamSourceAddress.Get()] = b;
    }

    Ipv4GlobalRoutingHelper::PopulateRoutingTables();

    std::vector<BeamRuntimeState> beams(nBeams);

    for (uint32_t b = 0; b < nBeams; ++b)
    {
        double userPayloadRateMbps = (b == hotspotBeam) ? hotspotUserRateMbps : baseUserRateMbps;
        double aggregatePayloadRateMbps = userPayloadRateMbps * static_cast<double>(nUsersPerBeam);

        double aggregateIpMbps =
            aggregatePayloadRateMbps *
            (static_cast<double>(packetSize) + 28.0) /
            static_cast<double>(packetSize);

        beams[b].beamId = b;
        beams[b].offeredPayloadMbps = aggregatePayloadRateMbps;
        beams[b].offeredIpMbps = aggregateIpMbps;
    }

    ApplicationContainer serverApps;

    for (uint32_t b = 0; b < nBeams; ++b)
    {
        uint16_t sinkPort = 9000 + b;
        UdpServerHelper server(sinkPort);

        ApplicationContainer app = server.Install(satellite.Get(0));
        app.Start(Seconds(0.0));
        app.Stop(Seconds(appStartTime + simTime + drainTime));

        serverApps.Add(app);
    }

    for (uint32_t b = 0; b < nBeams; ++b)
    {
        double aggregatePayloadRateMbps = beams[b].offeredPayloadMbps;
        double intervalSeconds =
            (static_cast<double>(packetSize) * 8.0) / (aggregatePayloadRateMbps * 1e6);

        uint16_t sinkPort = 9000 + b;

        UdpClientHelper client(p2pIfaces[b].GetAddress(0), sinkPort);
        client.SetAttribute("MaxPackets", UintegerValue(1000000000));
        client.SetAttribute("Interval", TimeValue(Seconds(intervalSeconds)));
        client.SetAttribute("PacketSize", UintegerValue(packetSize));

        ApplicationContainer app = client.Install(beamSources.Get(b));
        app.Start(Seconds(appStartTime + 0.005 * b));
        app.Stop(Seconds(appStartTime + simTime));
    }

    std::ofstream history("leo-multibeam-dynamic-history.csv");
    history << "time_s,"
            << "beam_id,"
            << "policy,"
            << "offered_payload_mbps,"
            << "offered_ip_mbps,"
            << "virtual_backlog_mb,"
            << "allocated_channels,"
            << "beam_capacity_mbps,"
            << "estimated_served_mb,"
            << "estimated_utilization,"
            << "ewma_served_mbps\n";

    Simulator::Schedule(Seconds(0.0),
                        &ControlStep,
                        &beams,
                        &satelliteDevices,
                        &sourceDevices,
                        &history,
                        policy,
                        totalChannels,
                        maxChannelsPerBeam,
                        minChannelsPerActiveBeam,
                        channelCapacityMbps,
                        controlInterval,
                        0.0,
                        simTime,
                        0);

    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> monitor = flowmonHelper.InstallAll();

    Simulator::Stop(Seconds(appStartTime + simTime + drainTime));
    Simulator::Run();

    history.close();

    monitor->CheckForLostPackets();

    Ptr<Ipv4FlowClassifier> classifier =
        DynamicCast<Ipv4FlowClassifier>(flowmonHelper.GetClassifier());

    std::map<uint32_t, BeamFlowMetrics> beamMetrics;

    for (const auto& flow : monitor->GetFlowStats())
    {
        Ipv4FlowClassifier::FiveTuple tuple = classifier->FindFlow(flow.first);

        auto it = addressToBeam.find(tuple.sourceAddress.Get());

        if (it == addressToBeam.end())
        {
            continue;
        }

        uint32_t beamId = it->second;
        BeamFlowMetrics& m = beamMetrics[beamId];

        m.txPackets += flow.second.txPackets;
        m.rxPackets += flow.second.rxPackets;
        m.lostPackets += flow.second.lostPackets;
        m.txBytes += flow.second.txBytes;
        m.rxBytes += flow.second.rxBytes;
        m.delaySumSeconds += flow.second.delaySum.GetSeconds();

        if (flow.second.txPackets > 0)
        {
            m.firstTx = std::min(m.firstTx, flow.second.timeFirstTxPacket.GetSeconds());
        }

        if (flow.second.rxPackets > 0)
        {
            m.lastRx = std::max(m.lastRx, flow.second.timeLastRxPacket.GetSeconds());
        }
    }

    std::ofstream csv("leo-multibeam-dynamic-final.csv");

    csv << "beam_id,"
        << "policy,"
        << "offered_payload_mbps,"
        << "offered_ip_mbps,"
        << "rx_mbps,"
        << "rx_mbps_observed_window,"
        << "measurement_window_s,"
        << "demand_satisfaction,"
        << "tx_packets,"
        << "rx_packets,"
        << "lost_packets,"
        << "delivery_ratio,"
        << "loss_rate,"
        << "mean_delay_ms,"
        << "final_virtual_backlog_mb,"
        << "last_allocated_channels,"
        << "last_beam_capacity_mbps,"
        << "ewma_served_mbps\n";

    std::cout << "\n=== LEO multibeam dynamic v3 final results ===\n";
    std::cout << "beam_id, policy, offered_payload_mbps, offered_ip_mbps, rx_mbps, "
                 "rx_mbps_observed_window, measurement_window_s, demand_satisfaction, "
                 "tx_packets, rx_packets, lost_packets, delivery_ratio, loss_rate, "
                 "mean_delay_ms, final_virtual_backlog_mb, last_allocated_channels, "
                 "last_beam_capacity_mbps, ewma_served_mbps\n";

    std::vector<double> throughputPerBeam;

    double totalRxMbps = 0.0;
    double totalOfferedIpMbps = 0.0;
    double sumFinalBacklogMb = 0.0;
    double maxFinalBacklogMb = 0.0;

    uint64_t totalTxPackets = 0;
    uint64_t totalRxPackets = 0;
    uint64_t totalLostPackets = 0;

    double weightedDelaySumSeconds = 0.0;

    for (uint32_t b = 0; b < nBeams; ++b)
    {
        BeamFlowMetrics m = beamMetrics[b];

        double measurementWindow = simTime;

        if (m.rxPackets > 0 &&
            m.firstTx < std::numeric_limits<double>::max() &&
            m.lastRx > m.firstTx)
        {
            measurementWindow = m.lastRx - m.firstTx;
        }

        double rxMbps = (m.rxBytes * 8.0) / simTime / 1e6;

        double rxMbpsObservedWindow = 0.0;
        if (measurementWindow > 0.0)
        {
            rxMbpsObservedWindow = (m.rxBytes * 8.0) / measurementWindow / 1e6;
        }

        double demandSatisfaction = 0.0;
        if (beams[b].offeredIpMbps > 0.0)
        {
            demandSatisfaction = rxMbps / beams[b].offeredIpMbps;
        }

        double deliveryRatio = 0.0;
        double lossRate = 0.0;
        double meanDelayMs = 0.0;

        if (m.txPackets > 0)
        {
            deliveryRatio = static_cast<double>(m.rxPackets) / static_cast<double>(m.txPackets);
            lossRate = 1.0 - deliveryRatio;
        }

        if (m.rxPackets > 0)
        {
            meanDelayMs = (m.delaySumSeconds / static_cast<double>(m.rxPackets)) * 1000.0;
        }

        throughputPerBeam.push_back(rxMbps);

        totalRxMbps += rxMbps;
        totalOfferedIpMbps += beams[b].offeredIpMbps;

        totalTxPackets += m.txPackets;
        totalRxPackets += m.rxPackets;
        totalLostPackets += m.lostPackets;

        weightedDelaySumSeconds += m.delaySumSeconds;

        sumFinalBacklogMb += beams[b].virtualBacklogMb;
        maxFinalBacklogMb = std::max(maxFinalBacklogMb, beams[b].virtualBacklogMb);

        csv << b << ","
            << policy << ","
            << std::fixed << std::setprecision(6)
            << beams[b].offeredPayloadMbps << ","
            << beams[b].offeredIpMbps << ","
            << rxMbps << ","
            << rxMbpsObservedWindow << ","
            << measurementWindow << ","
            << demandSatisfaction << ","
            << m.txPackets << ","
            << m.rxPackets << ","
            << m.lostPackets << ","
            << deliveryRatio << ","
            << lossRate << ","
            << meanDelayMs << ","
            << beams[b].virtualBacklogMb << ","
            << beams[b].allocatedChannels << ","
            << beams[b].beamCapacityMbps << ","
            << beams[b].ewmaServedMbps << "\n";

        std::cout << b << ", "
                  << policy << ", "
                  << std::fixed << std::setprecision(6)
                  << beams[b].offeredPayloadMbps << ", "
                  << beams[b].offeredIpMbps << ", "
                  << rxMbps << ", "
                  << rxMbpsObservedWindow << ", "
                  << measurementWindow << ", "
                  << demandSatisfaction << ", "
                  << m.txPackets << ", "
                  << m.rxPackets << ", "
                  << m.lostPackets << ", "
                  << deliveryRatio << ", "
                  << lossRate << ", "
                  << meanDelayMs << ", "
                  << beams[b].virtualBacklogMb << ", "
                  << beams[b].allocatedChannels << ", "
                  << beams[b].beamCapacityMbps << ", "
                  << beams[b].ewmaServedMbps << "\n";
    }

    csv.close();

    double fairness = JainFairness(throughputPerBeam);

    double globalDeliveryRatio = 0.0;
    double globalLossRate = 0.0;
    double globalMeanDelayMs = 0.0;
    double globalDemandSatisfaction = 0.0;
    double avgFinalBacklogMb = sumFinalBacklogMb / static_cast<double>(nBeams);

    if (totalTxPackets > 0)
    {
        globalDeliveryRatio = static_cast<double>(totalRxPackets) / static_cast<double>(totalTxPackets);
        globalLossRate = 1.0 - globalDeliveryRatio;
    }

    if (totalRxPackets > 0)
    {
        globalMeanDelayMs =
            (weightedDelaySumSeconds / static_cast<double>(totalRxPackets)) * 1000.0;
    }

    if (totalOfferedIpMbps > 0.0)
    {
        globalDemandSatisfaction = totalRxMbps / totalOfferedIpMbps;
    }

    std::ofstream summary("leo-multibeam-dynamic-summary.txt");
    summary << "version=dynamic_v3\n";
    summary << "policy=" << policy << "\n";
    summary << "nBeams=" << nBeams << "\n";
    summary << "nUsersPerBeam=" << nUsersPerBeam << "\n";
    summary << "hotspotBeam=" << hotspotBeam << "\n";
    summary << "simTime=" << simTime << "\n";
    summary << "controlInterval=" << controlInterval << "\n";
    summary << "baseUserRateMbps=" << baseUserRateMbps << "\n";
    summary << "hotspotUserRateMbps=" << hotspotUserRateMbps << "\n";
    summary << "totalChannels=" << totalChannels << "\n";
    summary << "maxChannelsPerBeam=" << maxChannelsPerBeam << "\n";
    summary << "minChannelsPerActiveBeam=" << minChannelsPerActiveBeam << "\n";
    summary << "channelCapacityMbps=" << channelCapacityMbps << "\n";
    summary << "total_offered_ip_mbps=" << totalOfferedIpMbps << "\n";
    summary << "total_rx_mbps=" << totalRxMbps << "\n";
    summary << "global_demand_satisfaction=" << globalDemandSatisfaction << "\n";
    summary << "global_delivery_ratio=" << globalDeliveryRatio << "\n";
    summary << "global_loss_rate=" << globalLossRate << "\n";
    summary << "global_mean_delay_ms=" << globalMeanDelayMs << "\n";
    summary << "avg_final_virtual_backlog_mb=" << avgFinalBacklogMb << "\n";
    summary << "max_final_virtual_backlog_mb=" << maxFinalBacklogMb << "\n";
    summary << "jain_fairness_rx_mbps=" << fairness << "\n";
    summary.close();

    std::cout << "\nTotal offered IP Mbps: " << std::fixed << std::setprecision(6)
              << totalOfferedIpMbps << "\n";
    std::cout << "Total rx_mbps: " << totalRxMbps << "\n";
    std::cout << "Global demand satisfaction: " << globalDemandSatisfaction << "\n";
    std::cout << "Global delivery ratio: " << globalDeliveryRatio << "\n";
    std::cout << "Global loss rate: " << globalLossRate << "\n";
    std::cout << "Global mean delay ms: " << globalMeanDelayMs << "\n";
    std::cout << "Avg final virtual backlog MB: " << avgFinalBacklogMb << "\n";
    std::cout << "Max final virtual backlog MB: " << maxFinalBacklogMb << "\n";
    std::cout << "Jain fairness over beam rx_mbps: " << fairness << "\n";

    std::cout << "History saved to: leo-multibeam-dynamic-history.csv\n";
    std::cout << "Final CSV saved to: leo-multibeam-dynamic-final.csv\n";
    std::cout << "Summary saved to: leo-multibeam-dynamic-summary.txt\n";

    Simulator::Destroy();

    return 0;
}
