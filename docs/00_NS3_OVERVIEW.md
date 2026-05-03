# Frente NS-3 do TCC LEO — Pacote de MDS Consolidados

Este pacote reúne a documentação consolidada da frente NS-3 do TCC sobre alocação dinâmica de canais em redes de satélites LEO multifeixe. A documentação foi revisada a partir dos arquivos enviados no pacote `tcc-neo-ns3.zip`, incluindo os CSVs consolidados, tabelas revisadas, scripts de campanha e figuras da pasta `figures_publication`.

Esta revisão também incorpora o arquivo-fonte final `leo-multibeam-dynamic.cc`, enviado posteriormente, permitindo documentar a implementação NS-3 com base direta no código consolidado.

## Arquivos incluídos

1. `01_NS3_SYSTEM_DEVELOPED.md`
2. `02_NS3_RESULTS_AND_ANALYSIS.md`
3. `03_NS3_EXECUTION_GUIDE.md`
4. `04_NS3_FIGURES_AND_TABLES_GUIDE.md`
5. `05_NS3_LATEX_TABLES.md`
6. `06_NS3_PYTHON_ALIGNMENT.md`
7. `leo-multibeam-dynamic.cc`

## Papel da frente NS-3

A frente NS-3 foi desenvolvida como uma verificação complementar da frente Python. Enquanto o simulador Python é o ambiente principal de decisão, filas, bloqueio, timeout, heurísticas e PPO, a frente NS-3 observa como políticas de alocação se manifestam em nível de rede, por meio de vazão recebida, perda de pacotes, atraso médio, backlog virtual e satisfação de demanda.

A frente NS-3 não substitui o simulador Python. Seu papel é aumentar a robustez metodológica do TCC ao mostrar que a redistribuição dinâmica de canais também produz efeitos coerentes quando a alocação é traduzida para capacidade de enlace em uma simulação de pacotes.

## Versão consolidada

A versão consolidada é:

```text
dynamic_v3
```

Arquivo NS-3 esperado:

```text
~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

Arquivo-fonte revisado nesta consolidação:

```text
leo-multibeam-dynamic.cc
```

Identificação do arquivo revisado:

```text
NS_LOG_COMPONENT_DEFINE("LeoMultibeamDynamicV3")
version=dynamic_v3
SHA-256: dbf2477b9c7b46065217318467a523e54996bdd1d7abb8f4071ee73c3eabb2cf
```

O arquivo deve ser copiado para o diretório `scratch` do NS-3 antes da execução das campanhas.

## Base numérica revisada

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

## Scripts catalogados

- `scripts/run_dynamic_v3_campaign.py`
- `scripts/collect_dynamic_v3_results.py`
- `scripts/plot_dynamic_v3_results.py`
- `scripts/make_dynamic_v3_tables.py`
- `scripts/plot_dynamic_v3_publication.py`

## Base gráfica revisada

- `analysis/dynamic_v3_campaign/figures_publication/01_vazao_total_mbps.png`
- `analysis/dynamic_v3_campaign/figures_publication/02_satisfacao_global_demanda.png`
- `analysis/dynamic_v3_campaign/figures_publication/03_taxa_perda_global.png`
- `analysis/dynamic_v3_campaign/figures_publication/04_atraso_medio_global_ms.png`
- `analysis/dynamic_v3_campaign/figures_publication/05_backlog_medio_final_mb.png`
- `analysis/dynamic_v3_campaign/figures_publication/06_backlog_maximo_final_mb.png`
- `analysis/dynamic_v3_campaign/figures_publication/07_satisfacao_hotspot.png`
- `analysis/dynamic_v3_campaign/figures_publication/08_perda_hotspot.png`
- `analysis/dynamic_v3_campaign/figures_publication/09_backlog_hotspot_mb.png`
- `analysis/dynamic_v3_campaign/figures_publication/10_fairness_jain.png`
- `analysis/dynamic_v3_campaign/figures_publication/11_hotspot_vs_normal_leve.png`
- `analysis/dynamic_v3_campaign/figures_publication/11_hotspot_vs_normal_medio.png`
- `analysis/dynamic_v3_campaign/figures_publication/11_hotspot_vs_normal_pesado_controlado.png`

## Cenários principais

| Cenário           |   Taxa base por usuário (Mbps) |   Taxa hotspot por usuário (Mbps) |   Carga IP total ofertada (Mbps) | Papel experimental                                             |
|:------------------|-------------------------------:|----------------------------------:|---------------------------------:|:---------------------------------------------------------------|
| Leve              |                            0.3 |                               1   |                          26.3168 | Operação com folga de capacidade                               |
| Médio             |                            0.5 |                               2   |                          45.232  | Cenário principal com hotspot moderado                         |
| Pesado Controlado |                            0.6 |                               2.5 |                          54.6896 | Carga pesada controlada, levemente acima da capacidade nominal |

A capacidade nominal total do sistema é:

```text
48 canais × 1.1 Mbps = 52.8 Mbps
```

Com isso, os cenários representam três regimes: folga de capacidade, pressão moderada por hotspot e carga pesada controlada levemente acima da capacidade nominal.

## Síntese dos resultados revisados

A leitura consolidada dos CSVs indica que:

- as políticas `Equal` e `Round Robin` funcionam como baselines simples, mas deixam o hotspot subatendido;
- `Longest Queue First` e `Proportional Fair` apresentam o melhor equilíbrio entre satisfação de demanda, perda, atraso e backlog;
- `Greedy Backlog` alcança vazão próxima às melhores políticas, mas tende a produzir atraso maior;
- a fairness de Jain deve ser tratada como métrica complementar, pois uma distribuição mais uniforme de vazão nem sempre significa melhor atendimento da demanda assimétrica;
- o cenário `heavy_controlled` é o cenário mais informativo para observar saturação controlada sem recorrer ao estresse extremo.

## Arquivos e pastas deprecated

Os seguintes diretórios foram úteis para validação incremental, mas não devem ser usados como base principal dos resultados do TCC:

- `results/basic_fixed/`
- `results/basic_agg/`
- `results/dynamic_v1/`
- `results/dynamic_v1_capacity_1_1/`
- `results/dynamic_v2/`
- `results/dynamic_v3/`
- `results/dynamic_v3_heavy_controlled/`
- `results/dynamic_v3_stress/`

O diretório principal para análise é:

```text
results/dynamic_v3_campaign/
```

O diretório principal para tabelas e gráficos revisados é:

```text
analysis/dynamic_v3_campaign/
```
