# Figuras, Tabelas e Arquivos-base — Frente NS-3

## 1. Arquivos numéricos centrais

- `analysis/dynamic_v3_campaign/summary_by_policy.csv`
- `analysis/dynamic_v3_campaign/beam_results.csv`
- `analysis/dynamic_v3_campaign/scenario_rankings.csv`
- `analysis/dynamic_v3_campaign/tables/tabela_resumo_metricas.csv`
- `analysis/dynamic_v3_campaign/tables/tabela_ranking_cenarios.csv`

## 2. Tabelas consolidadas a usar no texto

### Tabela 1 — resumo de métricas por cenário e política

Arquivo: `analysis/dynamic_v3_campaign/tables/tabela_resumo_metricas.csv`

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

### Tabela 2 — ranking de políticas por cenário

Arquivo: `analysis/dynamic_v3_campaign/tables/tabela_ranking_cenarios.csv`

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

## 3. Figuras corretas a inserir

| Arquivo                                    | Uso recomendado                                    |
|:-------------------------------------------|:---------------------------------------------------|
| 01_vazao_total_mbps.png                    | Principal — comparação de vazão total              |
| 02_satisfacao_global_demanda.png           | Principal — comparação de satisfação global        |
| 03_taxa_perda_global.png                   | Principal — comparação de perda global             |
| 04_atraso_medio_global_ms.png              | Principal — comparação de atraso médio             |
| 05_backlog_medio_final_mb.png              | Complementar — backlog médio final                 |
| 06_backlog_maximo_final_mb.png             | Principal — backlog máximo final                   |
| 07_satisfacao_hotspot.png                  | Principal — satisfação do hotspot                  |
| 08_perda_hotspot.png                       | Complementar — perda do hotspot                    |
| 09_backlog_hotspot_mb.png                  | Principal — backlog do hotspot                     |
| 10_fairness_jain.png                       | Complementar — fairness de Jain                    |
| 11_hotspot_vs_normal_leve.png              | Complementar — comparação hotspot vs beams normais |
| 11_hotspot_vs_normal_medio.png             | Complementar — comparação hotspot vs beams normais |
| 11_hotspot_vs_normal_pesado_controlado.png | Complementar — comparação hotspot vs beams normais |

## 4. Figuras principais recomendadas

Para o texto principal do TCC, recomenda-se usar:

1. `01_vazao_total_mbps.png`;
2. `02_satisfacao_global_demanda.png`;
3. `03_taxa_perda_global.png`;
4. `04_atraso_medio_global_ms.png`;
5. `06_backlog_maximo_final_mb.png`;
6. `07_satisfacao_hotspot.png`;
7. `09_backlog_hotspot_mb.png`.

## 5. Figuras complementares

- `05_backlog_medio_final_mb.png`;
- `08_perda_hotspot.png`;
- `10_fairness_jain.png`;
- `11_hotspot_vs_normal_leve.png`;
- `11_hotspot_vs_normal_medio.png`;
- `11_hotspot_vs_normal_pesado_controlado.png`.

## 6. Como citar os resultados corretamente

- Use a Tabela 1 para apresentar valores consolidados.
- Use a Tabela 2 para justificar o ranking das políticas.
- Use as figuras 1–4 para discutir desempenho global.
- Use as figuras 6, 7 e 9 para discutir o hotspot.
- Use fairness apenas como apoio, não como métrica principal.

## 7. Observação sobre fairness

A fairness de Jain mede equilíbrio de vazão entre beams. Em cenários com hotspot, uma política pode ter fairness mais baixa porque atende mais o beam com maior demanda. Portanto, fairness alta não significa necessariamente melhor política.

## 8. Observação sobre o cenário extremo

O cenário `dynamic_v3_stress` não pertence ao conjunto principal de resultados. Ele deve ser tratado como teste de limite.
