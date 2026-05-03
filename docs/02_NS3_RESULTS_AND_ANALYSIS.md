# Resultados e Análise — Frente NS-3

## 1. Base revisada desta análise

Esta análise foi revisada com base nos CSVs consolidados, nas tabelas finais e nas figuras `figures_publication` do pacote NS-3. Os arquivos centrais usados foram:

- `analysis/dynamic_v3_campaign/summary_by_policy.csv`
- `analysis/dynamic_v3_campaign/beam_results.csv`
- `analysis/dynamic_v3_campaign/scenario_rankings.csv`
- `analysis/dynamic_v3_campaign/tables/tabela_resumo_metricas.csv`
- `analysis/dynamic_v3_campaign/tables/tabela_ranking_cenarios.csv`
- `results/dynamic_v3_campaign/light/summary_*.txt`
- `results/dynamic_v3_campaign/medium/summary_*.txt`
- `results/dynamic_v3_campaign/heavy_controlled/summary_*.txt`
- `results/dynamic_v3_campaign/*/final_*.csv`
- `results/dynamic_v3_campaign/*/history_*.csv`

As figuras revisadas consideradas estão em:

```text
analysis/dynamic_v3_campaign/figures_publication/
```

## 2. Configuração geral dos experimentos

Todos os cenários principais usam:

- `nBeams = 19`;
- `nUsersPerBeam = 4`;
- `hotspotBeam = 0`;
- `simTime = 120 s`;
- `controlInterval = 1 s`;
- `totalChannels = 48`;
- `maxChannelsPerBeam = 6`;
- `minChannelsPerActiveBeam = 1`;
- `channelCapacityMbps = 1.1`.

A capacidade nominal total é:

```text
48 × 1.1 Mbps = 52.8 Mbps
```

A Tabela 1 resume os cenários usados.

### Tabela 1 — Cenários da campanha `dynamic_v3`

| Cenário           |   Taxa base por usuário (Mbps) |   Taxa hotspot por usuário (Mbps) |   Carga IP total ofertada (Mbps) | Papel experimental                                             |
|:------------------|-------------------------------:|----------------------------------:|---------------------------------:|:---------------------------------------------------------------|
| Leve              |                            0.3 |                               1   |                          26.3168 | Operação com folga de capacidade                               |
| Médio             |                            0.5 |                               2   |                          45.232  | Cenário principal com hotspot moderado                         |
| Pesado Controlado |                            0.6 |                               2.5 |                          54.6896 | Carga pesada controlada, levemente acima da capacidade nominal |

## 3. Leitura geral dos resultados

A Tabela 2 apresenta o resumo consolidado das principais métricas por cenário e política.

### Tabela 2 — Resumo consolidado das métricas NS-3

| Cenário           | Política            |   Vazão total (Mbps) |   Satisfação global (%) |   Perda global (%) |   Atraso médio global (ms) |   Backlog máximo final (MB) |   Satisfação hotspot (%) |   Backlog hotspot final (MB) |
|:------------------|:--------------------|---------------------:|------------------------:|-------------------:|---------------------------:|----------------------------:|-------------------------:|-----------------------------:|
| Leve              | Equal               |               23.641 |                  89.834 |             10.138 |                    343.457 |                      12.18  |                   35.137 |                       12.18  |
| Leve              | Round Robin         |               22.821 |                  86.716 |             13.256 |                    169.976 |                      20.292 |                   15.187 |                       20.292 |
| Leve              | Longest Queue First |               26.308 |                  99.968 |              0     |                     23.004 |                       0     |                  100     |                        0     |
| Leve              | Greedy Backlog      |               26.308 |                  99.968 |              0     |                     40.408 |                       0.017 |                  100     |                        0     |
| Leve              | Proportional Fair   |               26.308 |                  99.968 |              0     |                     23.004 |                       0     |                  100     |                        0     |
| Médio             | Equal               |               37.474 |                  82.847 |             17.127 |                     90.268 |                      73.86  |                    5.833 |                       73.86  |
| Médio             | Round Robin         |               37.336 |                  82.544 |             17.431 |                     78.338 |                      81.972 |                    4.162 |                       81.972 |
| Médio             | Longest Queue First |               39.884 |                  88.176 |             11.796 |                    403.119 |                      24.36  |                   35.142 |                       24.36  |
| Médio             | Greedy Backlog      |               39.884 |                  88.176 |             11.796 |                    923.382 |                      24.36  |                   35.142 |                       24.36  |
| Médio             | Proportional Fair   |               39.884 |                  88.176 |             11.796 |                    403.119 |                      24.36  |                   35.142 |                       24.36  |
| Pesado Controlado | Equal               |               38.3   |                  70.032 |             29.947 |                   2226.14  |                     104.7   |                    4.098 |                      104.7   |
| Pesado Controlado | Round Robin         |               44.694 |                  81.724 |             18.252 |                    362.638 |                     112.812 |                    2.931 |                      112.812 |
| Pesado Controlado | Longest Queue First |               45.996 |                  84.103 |             15.872 |                    300.071 |                      55.2   |                   15.589 |                       55.2   |
| Pesado Controlado | Greedy Backlog      |               45.988 |                  84.09  |             15.884 |                    955.805 |                      55.2   |                   15.589 |                       55.2   |
| Pesado Controlado | Proportional Fair   |               45.996 |                  84.103 |             15.872 |                    300.071 |                      55.2   |                   15.589 |                       55.2   |

A leitura geral indica três padrões principais:

1. no cenário leve, as políticas adaptativas atendem praticamente toda a demanda;
2. no cenário médio, as políticas adaptativas reduzem perda e backlog em relação aos baselines;
3. no cenário pesado controlado, `Longest Queue First` e `Proportional Fair` mantêm o melhor equilíbrio geral.

## 4. Cenário leve

O cenário leve possui carga IP total ofertada de **26.3168 Mbps**, bastante abaixo da capacidade nominal de **52.8 Mbps**. Nesse regime, existe folga global de capacidade, mas ainda há assimetria local causada pelo hotspot.

As políticas `Longest Queue First`, `Greedy Backlog` e `Proportional Fair` atingiram satisfação global de aproximadamente **99.968%** e perda global nula. O hotspot também foi plenamente atendido nessas três políticas, com satisfação de **100%**.

As políticas `Equal` e `Round Robin` apresentaram vazão menor e pior satisfação do hotspot. `Equal` atingiu satisfação hotspot de **35.137%**, enquanto `Round Robin` ficou em **15.187%**. Isso mostra que a simples existência de capacidade total disponível não garante bom atendimento ao hotspot quando a política não considera a distribuição espacial da demanda.

A fairness de Jain foi maior nas políticas uniformes, mas isso não representa melhor atendimento da demanda. No cenário leve, as políticas adaptativas concentram mais vazão no hotspot, o que reduz a igualdade de vazão entre beams, mas melhora a satisfação real da demanda.

## 5. Cenário médio

O cenário médio possui carga IP total ofertada de **45.232 Mbps**, abaixo da capacidade nominal total, mas com pressão localizada no hotspot. Esse é o cenário principal da frente NS-3.

`Equal` e `Round Robin` ficaram próximas em vazão total, com **37.474 Mbps** e **37.336 Mbps**, respectivamente. No entanto, ambas deixaram o hotspot fortemente subatendido, com satisfação de apenas **5.833%** em `Equal` e **4.162%** em `Round Robin`.

As políticas `Longest Queue First`, `Greedy Backlog` e `Proportional Fair` alcançaram **39.884 Mbps** de vazão total e satisfação global de **88.176%**, contra aproximadamente **82.8%** dos baselines. Também reduziram o backlog final do hotspot de **73.86 MB** ou **81.972 MB** para **24.36 MB**.

A diferença principal entre essas três políticas adaptativas está no atraso. `Greedy Backlog` manteve a mesma vazão e a mesma satisfação global, mas elevou o atraso médio global para **923.382 ms**, enquanto `Longest Queue First` e `Proportional Fair` ficaram em **403.119 ms**. Isso reforça que uma política agressiva pode melhorar atendimento, mas com maior custo temporal.

## 6. Cenário pesado controlado

O cenário pesado controlado possui carga IP total ofertada de **54.6896 Mbps**, levemente acima da capacidade nominal total de **52.8 Mbps**. Portanto, alguma perda e backlog são esperados.

`Equal` apresentou o pior desempenho geral, com satisfação global de **70.032%**, perda global de **29.947%** e atraso médio de **2226.140 ms**. `Round Robin` melhorou a vazão e reduziu a perda, mas ainda deixou o hotspot com backlog final de **112.812 MB** e satisfação hotspot de apenas **2.931%**.

`Longest Queue First` e `Proportional Fair` obtiveram os melhores resultados: **45.996 Mbps** de vazão total, **84.103%** de satisfação global, **15.872%** de perda global, **300.071 ms** de atraso médio e backlog máximo de **55.2 MB**. Essas duas políticas empataram nos principais indicadores globais.

`Greedy Backlog` ficou muito próximo em vazão e satisfação, com **45.988 Mbps** e **84.090%**, mas gerou atraso médio de **955.805 ms**. Assim, ele é competitivo em vazão, mas inferior em estabilidade temporal.

## 7. Ranking consolidado por cenário

A Tabela 3 apresenta o ranking gerado pela infraestrutura de análise. O `score_composto` combina ranking de satisfação global, perda global e atraso médio. Valores menores indicam melhor posição relativa.

### Tabela 3 — Ranking consolidado por cenário

| Cenário           | Política            |   Vazão total (Mbps) |   Satisfação global (%) |   Perda global (%) |   Atraso médio global (ms) |   Backlog máximo final (MB) |   Satisfação hotspot (%) |   Backlog hotspot final (MB) |   score_composto |
|:------------------|:--------------------|---------------------:|------------------------:|-------------------:|---------------------------:|----------------------------:|-------------------------:|-----------------------------:|-----------------:|
| Leve              | Longest Queue First |               26.308 |                  99.968 |              0     |                     23.004 |                       0     |                  100     |                        0     |                3 |
| Leve              | Proportional Fair   |               26.308 |                  99.968 |              0     |                     23.004 |                       0     |                  100     |                        0     |                3 |
| Leve              | Greedy Backlog      |               26.308 |                  99.968 |              0     |                     40.408 |                       0.017 |                  100     |                        0     |                5 |
| Leve              | Equal               |               23.641 |                  89.834 |             10.138 |                    343.457 |                      12.18  |                   35.137 |                       12.18  |               13 |
| Leve              | Round Robin         |               22.821 |                  86.716 |             13.256 |                    169.976 |                      20.292 |                   15.187 |                       20.292 |               14 |
| Médio             | Longest Queue First |               39.884 |                  88.176 |             11.796 |                    403.119 |                      24.36  |                   35.142 |                       24.36  |                5 |
| Médio             | Proportional Fair   |               39.884 |                  88.176 |             11.796 |                    403.119 |                      24.36  |                   35.142 |                       24.36  |                5 |
| Médio             | Greedy Backlog      |               39.884 |                  88.176 |             11.796 |                    923.382 |                      24.36  |                   35.142 |                       24.36  |                7 |
| Médio             | Equal               |               37.474 |                  82.847 |             17.127 |                     90.268 |                      73.86  |                    5.833 |                       73.86  |               10 |
| Médio             | Round Robin         |               37.336 |                  82.544 |             17.431 |                     78.338 |                      81.972 |                    4.162 |                       81.972 |               11 |
| Pesado Controlado | Longest Queue First |               45.996 |                  84.103 |             15.872 |                    300.071 |                      55.2   |                   15.589 |                       55.2   |                3 |
| Pesado Controlado | Proportional Fair   |               45.996 |                  84.103 |             15.872 |                    300.071 |                      55.2   |                   15.589 |                       55.2   |                3 |
| Pesado Controlado | Greedy Backlog      |               45.988 |                  84.09  |             15.884 |                    955.805 |                      55.2   |                   15.589 |                       55.2   |               10 |
| Pesado Controlado | Round Robin         |               44.694 |                  81.724 |             18.252 |                    362.638 |                     112.812 |                    2.931 |                      112.812 |               11 |
| Pesado Controlado | Equal               |               38.3   |                  70.032 |             29.947 |                   2226.14  |                     104.7   |                    4.098 |                      104.7   |               15 |

A leitura do ranking confirma que:

- `Longest Queue First` e `Proportional Fair` lideram em todos os cenários principais;
- `Greedy Backlog` é competitivo, mas perde posição por atraso maior;
- `Equal` e `Round Robin` são úteis como baselines, mas não são adequados para hotspot;
- em carga pesada controlada, as diferenças entre políticas se tornam mais evidentes.

## 8. Teste extremo de limite

O cenário extremo não foi incluído na campanha principal. Ele foi mantido apenas como teste de limite, com carga IP total de **71.5488 Mbps**, muito acima da capacidade nominal de **52.8 Mbps**.

### Tabela 4 — Cenário extremo como teste de limite

| Política            |   Carga IP ofertada (Mbps) |   Vazão total (Mbps) |   Satisfação global |   Perda global |   Atraso médio (ms) |   Backlog máximo (MB) |   Fairness Jain |
|:--------------------|---------------------------:|---------------------:|--------------------:|---------------:|--------------------:|----------------------:|----------------:|
| equal               |                     71.549 |               35.172 |               0.492 |          0.508 |             851.569 |               135.54  |           0.648 |
| greedy_backlog      |                     71.549 |               18.588 |               0.26  |          0.74  |            5451.44  |                86.04  |           0.996 |
| longest_queue_first |                     71.549 |               19.44  |               0.272 |          0.728 |            5268.1   |                86.04  |           0.998 |
| proportional_fair   |                     71.549 |               19.468 |               0.272 |          0.728 |            5252.17  |                86.315 |           0.998 |
| round_robin         |                     71.549 |               28.166 |               0.394 |          0.606 |            5204.84  |               143.653 |           0.961 |

Esse cenário mostra que a rede entra em saturação severa. Ele não deve ser usado como comparação principal entre políticas, pois sua função é apenas indicar comportamento sob sobrecarga extrema. A interpretação recomendada é tratá-lo como evidência de robustez/limite, não como cenário central do TCC.

## 9. Interpretação das métricas

### 9.1 Vazão total recebida

A vazão total mostra quanto tráfego foi efetivamente recebido. Ela é a métrica mais próxima do `goodput` usado na frente Python, embora não seja numericamente equivalente.

### 9.2 Satisfação global de demanda

A satisfação global é uma métrica central porque relaciona a vazão entregue com a carga ofertada. Ela permite comparar cenários com cargas diferentes.

### 9.3 Perda global

A perda global mede degradação em nível de pacote. Ela não é igual ao bloqueio da frente Python, mas desempenha papel análogo como indicador de atendimento insuficiente.

### 9.4 Atraso médio global

O atraso médio captura o custo temporal da política. `Greedy Backlog` mostra que maior vazão não significa necessariamente menor atraso.

### 9.5 Backlog virtual

O backlog virtual indica demanda acumulada não atendida. Ele é especialmente útil para avaliar o hotspot.

### 9.6 Fairness de Jain

A fairness de Jain deve ser lida como métrica complementar. Em cenários com hotspot, alta fairness de vazão pode significar apenas que a política distribuiu vazão de forma uniforme, não que atendeu corretamente a demanda assimétrica.

## 10. Síntese interpretativa

A frente NS-3 confirma que a alocação dinâmica de canais é relevante para ambientes LEO multifeixe com hotspot. Políticas uniformes tendem a desperdiçar capacidade relativa e deixam o beam mais carregado subatendido. Políticas adaptativas reduzem perda e backlog, aumentando a satisfação de demanda.

Entre as políticas avaliadas, `Longest Queue First` e `Proportional Fair` apresentaram o melhor equilíbrio geral. `Greedy Backlog` mostrou desempenho competitivo em vazão, mas atraso mais elevado. `Equal` e `Round Robin` cumprem bem o papel de baselines, mas não são suficientes para cenários com carga assimétrica.

## 11. Conclusão desta etapa

Os resultados da frente NS-3 são suficientes para sustentar uma etapa complementar do TCC. Eles não substituem os resultados da frente Python, mas reforçam a análise ao mostrar que a redistribuição dinâmica de canais também produz efeitos coerentes em métricas de rede como vazão, perda, atraso e backlog virtual.
