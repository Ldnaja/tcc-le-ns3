# Sistema Desenvolvido — Frente NS-3

## 1. Visão geral da frente NS-3

A frente NS-3 foi desenvolvida como a segunda frente experimental do TCC, com o objetivo de complementar o simulador Python por meio de uma simulação em nível de rede. Seu papel foi verificar como políticas de alocação dinâmica de canais se comportam quando a decisão de recurso passa a alterar a capacidade de enlaces e, consequentemente, métricas de pacotes como vazão recebida, perda e atraso.

A escolha por NS-3 teve três objetivos principais. O primeiro foi trazer uma camada de validação mais próxima de uma simulação de rede, sem transformar o TCC em uma modelagem orbital completa. O segundo foi observar efeitos que o simulador Python não mede diretamente, como perda de pacotes e atraso de rede. O terceiro foi manter alinhamento com o problema central já estudado em Python: redistribuição de canais em ambiente LEO multifeixe com carga assimétrica e hotspot.

Assim, a frente NS-3 não foi tratada como substituta da frente Python. Ela foi construída como uma verificação complementar, controlada e coerente com o escopo do TCC.

## 2. Objetivo técnico do sistema

O sistema NS-3 foi projetado para responder à seguinte pergunta:

> Quando políticas de alocação dinâmica redistribuem canais entre beams, quais efeitos aparecem em nível de rede sobre vazão, perda, atraso, backlog virtual e satisfação de demanda?

Para responder a essa questão, a versão `dynamic_v3` representa:

- uma rede multifeixe com 19 beams;
- 4 usuários agregados por beam;
- um hotspot fixo no beam 0;
- um total de 48 canais disponíveis;
- limite máximo de 6 canais por beam;
- mínimo de 1 canal por beam ativo;
- capacidade de 1.1 Mbps por canal;
- controle de alocação a cada 1 segundo;
- tráfego UDP agregado por beam;
- coleta de métricas via arquivos finais e históricos.

## 3. Arquitetura lógica da simulação

A simulação segue a sequência lógica abaixo:

1. os parâmetros de cenário e política são recebidos por linha de comando;
2. a topologia agregada de beams é criada;
3. cada beam recebe um fluxo de tráfego compatível com sua taxa de usuários;
4. o beam de hotspot recebe taxa superior à dos demais beams;
5. a política de alocação define quantos canais cada beam recebe em cada intervalo de controle;
6. a capacidade de cada enlace é atualizada a partir do número de canais alocados;
7. o tráfego é transmitido pela rede NS-3;
8. métricas por beam e globais são salvas em arquivos CSV e TXT;
9. scripts Python consolidam os resultados, geram rankings, tabelas e figuras.

## 3.1 Estruturas e funções principais do código C++

O arquivo `leo-multibeam-dynamic.cc` organiza a simulação em torno de duas estruturas principais:

- `BeamRuntimeState`: armazena o estado lógico de cada beam, incluindo carga ofertada, backlog virtual, canais alocados, capacidade do beam, serviço estimado, utilização estimada e média móvel de serviço (`ewmaServedMbps`).
- `BeamFlowMetrics`: armazena as métricas observadas pelo `FlowMonitor`, incluindo pacotes transmitidos, recebidos, perdidos, bytes transmitidos/recebidos e soma de atrasos.

As funções principais do modelo são:

- `JainFairness`: calcula o índice de Jain sobre a vazão por beam.
- `ActiveBeamIds`: identifica beams ativos com carga ou backlog.
- `GiveMinimumChannels`: garante o mínimo de canais por beam ativo, evitando starvation artificial.
- `InitialResidualPressureMb`: calcula a pressão inicial de demanda de cada beam como backlog acumulado mais demanda do passo atual.
- `AllocateChannels`: implementa as políticas `equal`, `round_robin`, `longest_queue_first`, `greedy_backlog` e `proportional_fair`.
- `ApplyLinkRates`: aplica a capacidade calculada ao enlace ponto-a-ponto correspondente.
- `ControlStep`: executa o ciclo de controle a cada intervalo, atualizando backlog, alocação, capacidade e histórico.

## 3.2 Parâmetros padrão definidos no código C++

A versão consolidada usa os seguintes valores padrão, que também podem ser sobrescritos por linha de comando:

| Parâmetro | Valor padrão | Função |
|---|---:|---|
| `nBeams` | 19 | número de beams lógicos |
| `nUsersPerBeam` | 4 | usuários representados em cada fluxo agregado |
| `hotspotBeam` | 0 | beam com maior carga |
| `simTime` | 120 s | duração da geração de tráfego |
| `appStartTime` | 1 s | início das aplicações |
| `drainTime` | 5 s | tempo adicional para escoamento |
| `controlInterval` | 1 s | intervalo de decisão de alocação |
| `baseUserRateMbps` | 0.50 Mbps | taxa por usuário em beams normais |
| `hotspotUserRateMbps` | 2.00 Mbps | taxa por usuário no hotspot |
| `totalChannels` | 48 | canais totais disponíveis |
| `maxChannelsPerBeam` | 6 | máximo de canais por beam |
| `minChannelsPerActiveBeam` | 1 | proteção mínima contra starvation |
| `channelCapacityMbps` | 1.1 Mbps | capacidade representada por canal |
| `initialBeamLinkRateMbps` | 1.0 Mbps | taxa inicial antes do controle dinâmico |
| `leoDelayMs` | 20 ms | atraso unidirecional do enlace |
| `packetSize` | 1000 bytes | tamanho do payload UDP |
| `policy` | `proportional_fair` | política padrão |

## 3.3 Modelo de tráfego e topologia no NS-3

A topologia é composta por um nó central representando o satélite e um conjunto de nós de origem, um por beam lógico. Cada beam é conectado ao nó central por um enlace ponto-a-ponto (`PointToPointHelper`). A taxa do enlace é atualizada dinamicamente conforme os canais alocados ao beam.

Cada beam gera tráfego UDP agregado. A taxa de payload agregada é calculada como:

```text
aggregatePayloadRateMbps = userPayloadRateMbps × nUsersPerBeam
```

A carga IP considerada pelo controle inclui overhead simplificado de 28 bytes sobre o payload UDP de 1000 bytes:

```text
aggregateIpMbps = aggregatePayloadRateMbps × (packetSize + 28) / packetSize
```

Isso explica por que `offered_ip_mbps` é ligeiramente maior que `offered_payload_mbps`.

## 3.4 Saídas geradas pelo código C++

Cada execução gera três arquivos no diretório do NS-3:

- `leo-multibeam-dynamic-history.csv`: histórico por tempo e beam, com backlog, canais alocados, capacidade e utilização estimada.
- `leo-multibeam-dynamic-final.csv`: métricas finais por beam, incluindo vazão, perda, atraso, satisfação de demanda e backlog final.
- `leo-multibeam-dynamic-summary.txt`: resumo global da execução, com cenário, política, vazão total, satisfação global, perda global, atraso médio, backlog e fairness.

Os scripts Python copiam esses arquivos para `results/dynamic_v3_campaign/<cenario>/` usando nomes específicos por política.

## 4. Organização dos arquivos

A infraestrutura Python da frente NS-3 fica fora da instalação do NS-3:

```text
~/tcc-leo-ns3/
├── scripts/
├── results/
├── analysis/
└── docs/
```

O código NS-3 fica no diretório `scratch` da instalação do simulador:

```text
~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

O arquivo-fonte `leo-multibeam-dynamic.cc` foi revisado nesta consolidação e corresponde à versão `dynamic_v3`. Ele deve ser mantido em:

```text
~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

Identificação do código revisado:

```text
NS_LOG_COMPONENT_DEFINE("LeoMultibeamDynamicV3")
summary version=dynamic_v3
SHA-256: dbf2477b9c7b46065217318467a523e54996bdd1d7abb8f4071ee73c3eabb2cf
```

## 5. Scripts da infraestrutura Python

### 5.1 `run_dynamic_v3_campaign.py`

Executa automaticamente campanhas NS-3. O script define os cenários `light`, `medium`, `heavy_controlled` e `extreme`, além das políticas `equal`, `round_robin`, `longest_queue_first`, `greedy_backlog` e `proportional_fair`.

O script chama o NS-3 com o programa:

```text
scratch/leo-multibeam-dynamic
```

Após cada execução, copia os arquivos:

- `leo-multibeam-dynamic-history.csv`
- `leo-multibeam-dynamic-final.csv`
- `leo-multibeam-dynamic-summary.txt`

para a pasta do respectivo cenário.

### 5.2 `collect_dynamic_v3_results.py`

Lê os arquivos `summary_*.txt` e `final_*.csv` de cada cenário e política. Em seguida, gera:

- `summary_by_policy.csv`
- `beam_results.csv`
- `scenario_rankings.csv`

Esse script também separa métricas do hotspot e métricas médias dos beams normais.

### 5.3 `make_dynamic_v3_tables.py`

Converte os CSVs consolidados em tabelas revisadas para análise e escrita. Ele gera arquivos em CSV, Markdown e LaTeX:

- `tabela_resumo_metricas.*`
- `tabela_ranking_cenarios.*`

### 5.4 `plot_dynamic_v3_publication.py`

Gera figuras revisadas em português, com ordem fixa de cenários e políticas. A saída principal fica em:

```text
analysis/dynamic_v3_campaign/figures_publication/
```

### 5.5 `plot_dynamic_v3_results.py`

Gera figuras diagnósticas. Como a pasta `figures` foi removida do pacote final, esse script deve ser tratado como apoio de depuração, não como fonte principal de figuras para o TCC.

## 6. Cenários implementados

| Cenário           |   Taxa base por usuário (Mbps) |   Taxa hotspot por usuário (Mbps) |   Carga IP total ofertada (Mbps) | Papel experimental                                             |
|:------------------|-------------------------------:|----------------------------------:|---------------------------------:|:---------------------------------------------------------------|
| Leve              |                            0.3 |                               1   |                          26.3168 | Operação com folga de capacidade                               |
| Médio             |                            0.5 |                               2   |                          45.232  | Cenário principal com hotspot moderado                         |
| Pesado Controlado |                            0.6 |                               2.5 |                          54.6896 | Carga pesada controlada, levemente acima da capacidade nominal |

A carga IP total ofertada considera overhead em relação ao payload configurado. Por isso, os valores de carga IP total são superiores à soma direta das taxas de payload.

## 7. Políticas implementadas

### 7.1 Equal

Distribui os canais de forma uniforme. É a baseline mais simples e não considera demanda, backlog ou histórico de atendimento.

### 7.2 Round Robin

Distribui os recursos de forma rotativa entre beams. Serve como baseline temporal, mas ainda não é orientada por carga.

### 7.3 Longest Queue First

Prioriza beams com maior backlog virtual. Na versão `dynamic_v3`, essa política apresentou comportamento estável e bom equilíbrio entre vazão, perda e atraso.

### 7.4 Greedy Backlog

Prioriza de forma mais agressiva beams com maior pressão de backlog. A política alcançou vazão semelhante às melhores, mas gerou atraso maior em cenários pressionados.

### 7.5 Proportional Fair

Busca equilíbrio entre demanda/backlog e histórico de atendimento. Foi uma das políticas mais consistentes e defensáveis para análise acadêmica.

## 8. Métricas geradas

As principais métricas globais são:

- `total_offered_ip_mbps`;
- `total_rx_mbps`;
- `global_demand_satisfaction`;
- `global_delivery_ratio`;
- `global_loss_rate`;
- `global_mean_delay_ms`;
- `avg_final_virtual_backlog_mb`;
- `max_final_virtual_backlog_mb`;
- `jain_fairness_rx_mbps`.

As principais métricas por beam são:

- `offered_payload_mbps`;
- `offered_ip_mbps`;
- `rx_mbps`;
- `rx_mbps_observed_window`;
- `demand_satisfaction`;
- `tx_packets`;
- `rx_packets`;
- `lost_packets`;
- `delivery_ratio`;
- `loss_rate`;
- `mean_delay_ms`;
- `final_virtual_backlog_mb`;
- `last_allocated_channels`;
- `last_beam_capacity_mbps`;
- `ewma_served_mbps`.

## 9. Modelo abstrato adotado

A frente NS-3 não implementa uma constelação orbital completa, handover, roteamento global, Doppler detalhado ou dinâmica orbital de satélites LEO. Essas escolhas foram intencionais para manter o escopo controlado.

A abstração adotada é uma simulação multifeixe agregada, na qual cada beam representa uma região de atendimento e a política de alocação altera a capacidade do enlace associado ao beam. Essa modelagem é adequada para observar os efeitos da redistribuição dinâmica de canais sem expandir o TCC para um projeto completo de mobilidade orbital.

## 10. Papel desta frente dentro do trabalho

A frente NS-3 cumpre três papéis principais:

1. verificar o problema de alocação em nível de rede;
2. observar perda, atraso e vazão sob alteração dinâmica de capacidade;
3. complementar os resultados da frente Python sem duplicar a implementação de RL.

O aprendizado por reforço permanece concentrado na frente Python. Implementar RL diretamente no NS-3 seria uma nova frente de pesquisa e foi considerado extenso demais para o escopo atual.
