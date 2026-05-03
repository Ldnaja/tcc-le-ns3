# Tabelas em LaTeX — Frente NS-3

Este documento reúne tabelas em LaTeX para a frente NS-3.

## Tabela 1 — Cenários da campanha NS-3

```latex
\begin{table}
\caption{Cenários da campanha NS-3 dynamic\_v3.}
\label{tab:ns3_scenarios}
\begin{tabular}{lrrrl}
\toprule
Cenário & Taxa base por usuário (Mbps) & Taxa hotspot por usuário (Mbps) & Carga IP total ofertada (Mbps) & Papel experimental \\
\midrule
Leve & 0.300000 & 1.000000 & 26.316800 & Operação com folga de capacidade \\
Médio & 0.500000 & 2.000000 & 45.232000 & Cenário principal com hotspot moderado \\
Pesado Controlado & 0.600000 & 2.500000 & 54.689600 & Carga pesada controlada, levemente acima da capacidade nominal \\
\bottomrule
\end{tabular}
\end{table}

```

## Tabela 2 — Resumo de métricas por cenário e política

```latex
\begin{longtable}{llrrrrrrrrrr}
\caption{Tabela Resumo Metricas} \label{tab:tabela_resumo_metricas} \\
\toprule
Cenário & Política & Vazão total (Mbps) & Satisfação global (\%) & Perda global (\%) & Atraso médio global (ms) & Backlog médio final (MB) & Backlog máximo final (MB) & Fairness Jain & Satisfação hotspot (\%) & Perda hotspot (\%) & Backlog hotspot final (MB) \\
\midrule
\endfirsthead
\caption[]{Tabela Resumo Metricas} \\
\toprule
Cenário & Política & Vazão total (Mbps) & Satisfação global (\%) & Perda global (\%) & Atraso médio global (ms) & Backlog médio final (MB) & Backlog máximo final (MB) & Fairness Jain & Satisfação hotspot (\%) & Perda hotspot (\%) & Backlog hotspot final (MB) \\
\midrule
\endhead
\midrule
\multicolumn{12}{r}{Continued on next page} \\
\midrule
\endfoot
\bottomrule
\endlastfoot
Leve & Equal & 23.641000 & 89.834000 & 10.138000 & 343.457000 & 0.641000 & 12.180000 & 0.999000 & 35.137000 & 64.863000 & 12.180000 \\
Leve & Round Robin & 22.821000 & 86.716000 & 13.256000 & 169.976000 & 1.068000 & 20.292000 & 0.987000 & 15.187000 & 84.813000 & 20.292000 \\
Leve & Longest Queue First & 26.308000 & 99.968000 & 0.000000 & 23.004000 & 0.000000 & 0.000000 & 0.823000 & 100.000000 & 0.000000 & 0.000000 \\
Leve & Greedy Backlog & 26.308000 & 99.968000 & 0.000000 & 40.408000 & 0.005000 & 0.017000 & 0.823000 & 100.000000 & 0.000000 & 0.000000 \\
Leve & Proportional Fair & 26.308000 & 99.968000 & 0.000000 & 23.004000 & 0.000000 & 0.000000 & 0.823000 & 100.000000 & 0.000000 & 0.000000 \\
Médio & Equal & 37.474000 & 82.847000 & 17.127000 & 90.268000 & 3.887000 & 73.860000 & 0.969000 & 5.833000 & 94.168000 & 73.860000 \\
Médio & Round Robin & 37.336000 & 82.544000 & 17.431000 & 78.338000 & 4.314000 & 81.972000 & 0.963000 & 4.162000 & 95.838000 & 81.972000 \\
Médio & Longest Queue First & 39.884000 & 88.176000 & 11.796000 & 403.119000 & 1.282000 & 24.360000 & 0.992000 & 35.142000 & 64.858000 & 24.360000 \\
Médio & Greedy Backlog & 39.884000 & 88.176000 & 11.796000 & 923.382000 & 1.433000 & 24.360000 & 0.992000 & 35.142000 & 64.858000 & 24.360000 \\
Médio & Proportional Fair & 39.884000 & 88.176000 & 11.796000 & 403.119000 & 1.282000 & 24.360000 & 0.992000 & 35.142000 & 64.858000 & 24.360000 \\
Pesado Controlado & Equal & 38.300000 & 70.032000 & 29.947000 & 2226.140000 & 7.409000 & 104.700000 & 0.939000 & 4.098000 & 95.902000 & 104.700000 \\
Pesado Controlado & Round Robin & 44.694000 & 81.724000 & 18.252000 & 362.638000 & 6.023000 & 112.812000 & 0.959000 & 2.931000 & 97.069000 & 112.812000 \\
Pesado Controlado & Longest Queue First & 45.996000 & 84.103000 & 15.872000 & 300.071000 & 2.937000 & 55.200000 & 0.994000 & 15.589000 & 84.411000 & 55.200000 \\
Pesado Controlado & Greedy Backlog & 45.988000 & 84.090000 & 15.884000 & 955.805000 & 3.121000 & 55.200000 & 0.994000 & 15.589000 & 84.411000 & 55.200000 \\
Pesado Controlado & Proportional Fair & 45.996000 & 84.103000 & 15.872000 & 300.071000 & 2.937000 & 55.200000 & 0.994000 & 15.589000 & 84.411000 & 55.200000 \\
\end{longtable}

```

## Tabela 3 — Ranking de políticas por cenário

```latex
\begin{longtable}{llrrrrrrrr}
\caption{Tabela Ranking Cenarios} \label{tab:tabela_ranking_cenarios} \\
\toprule
Cenário & Política & Vazão total (Mbps) & Satisfação global (\%) & Perda global (\%) & Atraso médio global (ms) & Backlog máximo final (MB) & Satisfação hotspot (\%) & Backlog hotspot final (MB) & score\_composto \\
\midrule
\endfirsthead
\caption[]{Tabela Ranking Cenarios} \\
\toprule
Cenário & Política & Vazão total (Mbps) & Satisfação global (\%) & Perda global (\%) & Atraso médio global (ms) & Backlog máximo final (MB) & Satisfação hotspot (\%) & Backlog hotspot final (MB) & score\_composto \\
\midrule
\endhead
\midrule
\multicolumn{10}{r}{Continued on next page} \\
\midrule
\endfoot
\bottomrule
\endlastfoot
Leve & Longest Queue First & 26.308000 & 99.968000 & 0.000000 & 23.004000 & 0.000000 & 100.000000 & 0.000000 & 3.000000 \\
Leve & Proportional Fair & 26.308000 & 99.968000 & 0.000000 & 23.004000 & 0.000000 & 100.000000 & 0.000000 & 3.000000 \\
Leve & Greedy Backlog & 26.308000 & 99.968000 & 0.000000 & 40.408000 & 0.017000 & 100.000000 & 0.000000 & 5.000000 \\
Leve & Equal & 23.641000 & 89.834000 & 10.138000 & 343.457000 & 12.180000 & 35.137000 & 12.180000 & 13.000000 \\
Leve & Round Robin & 22.821000 & 86.716000 & 13.256000 & 169.976000 & 20.292000 & 15.187000 & 20.292000 & 14.000000 \\
Médio & Longest Queue First & 39.884000 & 88.176000 & 11.796000 & 403.119000 & 24.360000 & 35.142000 & 24.360000 & 5.000000 \\
Médio & Proportional Fair & 39.884000 & 88.176000 & 11.796000 & 403.119000 & 24.360000 & 35.142000 & 24.360000 & 5.000000 \\
Médio & Greedy Backlog & 39.884000 & 88.176000 & 11.796000 & 923.382000 & 24.360000 & 35.142000 & 24.360000 & 7.000000 \\
Médio & Equal & 37.474000 & 82.847000 & 17.127000 & 90.268000 & 73.860000 & 5.833000 & 73.860000 & 10.000000 \\
Médio & Round Robin & 37.336000 & 82.544000 & 17.431000 & 78.338000 & 81.972000 & 4.162000 & 81.972000 & 11.000000 \\
Pesado Controlado & Longest Queue First & 45.996000 & 84.103000 & 15.872000 & 300.071000 & 55.200000 & 15.589000 & 55.200000 & 3.000000 \\
Pesado Controlado & Proportional Fair & 45.996000 & 84.103000 & 15.872000 & 300.071000 & 55.200000 & 15.589000 & 55.200000 & 3.000000 \\
Pesado Controlado & Greedy Backlog & 45.988000 & 84.090000 & 15.884000 & 955.805000 & 55.200000 & 15.589000 & 55.200000 & 10.000000 \\
Pesado Controlado & Round Robin & 44.694000 & 81.724000 & 18.252000 & 362.638000 & 112.812000 & 2.931000 & 112.812000 & 11.000000 \\
Pesado Controlado & Equal & 38.300000 & 70.032000 & 29.947000 & 2226.140000 & 104.700000 & 4.098000 & 104.700000 & 15.000000 \\
\end{longtable}

```

## Tabela 4 — Figuras revisadas da frente NS-3

```latex
\begin{table}
\caption{Figuras revisadas da frente NS-3.}
\label{tab:ns3_figures}
\begin{tabular}{ll}
\toprule
Arquivo & Uso recomendado \\
\midrule
01\_vazao\_total\_mbps.png & Principal — comparação de vazão total \\
02\_satisfacao\_global\_demanda.png & Principal — comparação de satisfação global \\
03\_taxa\_perda\_global.png & Principal — comparação de perda global \\
04\_atraso\_medio\_global\_ms.png & Principal — comparação de atraso médio \\
05\_backlog\_medio\_final\_mb.png & Complementar — backlog médio final \\
06\_backlog\_maximo\_final\_mb.png & Principal — backlog máximo final \\
07\_satisfacao\_hotspot.png & Principal — satisfação do hotspot \\
08\_perda\_hotspot.png & Complementar — perda do hotspot \\
09\_backlog\_hotspot\_mb.png & Principal — backlog do hotspot \\
10\_fairness\_jain.png & Complementar — fairness de Jain \\
11\_hotspot\_vs\_normal\_leve.png & Complementar — comparação hotspot vs beams normais \\
11\_hotspot\_vs\_normal\_medio.png & Complementar — comparação hotspot vs beams normais \\
11\_hotspot\_vs\_normal\_pesado\_controlado.png & Complementar — comparação hotspot vs beams normais \\
\bottomrule
\end{tabular}
\end{table}

```

## Tabela adicional — Cenário extremo como teste de limite

```latex
\begin{table}
\caption{Cenário extremo da frente NS-3 usado apenas como teste de limite.}
\label{tab:ns3_extreme_stress}
\begin{tabular}{lrrrrrrr}
\toprule
Política & Carga IP ofertada (Mbps) & Vazão total (Mbps) & Satisfação global & Perda global & Atraso médio (ms) & Backlog máximo (MB) & Fairness Jain \\
\midrule
equal & 71.549000 & 35.172000 & 0.492000 & 0.508000 & 851.569000 & 135.540000 & 0.648000 \\
greedy\_backlog & 71.549000 & 18.588000 & 0.260000 & 0.740000 & 5451.440000 & 86.040000 & 0.996000 \\
longest\_queue\_first & 71.549000 & 19.440000 & 0.272000 & 0.728000 & 5268.100000 & 86.040000 & 0.998000 \\
proportional\_fair & 71.549000 & 19.468000 & 0.272000 & 0.728000 & 5252.170000 & 86.315000 & 0.998000 \\
round\_robin & 71.549000 & 28.166000 & 0.394000 & 0.606000 & 5204.840000 & 143.653000 & 0.961000 \\
\bottomrule
\end{tabular}
\end{table}

```

## Observações de uso

- A Tabela 2 é larga e pode ser mais adequada em modo paisagem, `longtable` ou apêndice.
- Para o texto principal, pode ser melhor usar recortes por cenário.
- A fairness deve ser interpretada como métrica complementar.
- O cenário extremo não deve ser misturado aos cenários principais.
