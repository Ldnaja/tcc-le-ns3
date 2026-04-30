# Frente NS-3 — Alocação Dinâmica de Canais em Redes LEO Multifeixe

## 1. Objetivo da frente NS-3

Esta frente tem como objetivo complementar o simulador principal em Python do TCC, oferecendo uma verificação em nível de rede para o problema de alocação dinâmica de canais em um ambiente LEO multifeixe simplificado.

A frente Python é o ambiente principal de estudo de decisão, filas, bloqueio, timeout, heurísticas e aprendizado por reforço. A frente NS-3 não substitui essa modelagem. Ela verifica como a redistribuição dinâmica de canais se manifesta quando a capacidade dos enlaces é alterada em uma simulação de rede baseada em pacotes.

## 2. Diferença entre a frente Python e a frente NS-3

### 2.1 Frente Python

A frente Python trabalha em nível lógico e controlado. Ela modela:

- múltiplos beams;
- carga variável;
- hotspot;
- canais totais;
- máximo de canais por beam;
- filas por beam;
- bloqueio por fila máxima;
- descarte por timeout;
- heurísticas de alocação;
- agente PPO;
- métricas como goodput, bloqueio, atraso lógico, taxa de aceitação, utilização e fairness.

Essa frente é adequada para avaliar a lógica de decisão e comparar heurísticas em um ambiente controlado.

### 2.2 Frente NS-3

A frente NS-3 trabalha em nível de rede. Ela modela cada beam como um fluxo agregado e altera dinamicamente a capacidade do enlace associado ao beam.

Ela mede:

- vazão recebida;
- perda de pacotes;
- atraso médio;
- satisfação de demanda;
- backlog virtual;
- fairness sobre vazão;
- efeito da política de alocação sobre enlaces e pacotes.

Essa frente é adequada para verificar o comportamento das políticas quando a alocação se transforma em capacidade real de transmissão.

## 3. Interpretação metodológica

Os resultados da frente Python e da frente NS-3 não devem ser comparados como valores numéricos equivalentes.

A comparação correta é feita por tendência:

- políticas adaptativas reduzem backlog?
- políticas adaptativas aumentam satisfação de demanda?
- políticas uniformes sofrem em cenários com hotspot?
- políticas agressivas aumentam atraso?
- a saturação aparece como bloqueio no Python e como perda/atraso no NS-3?

No Python, bloqueio e timeout são eventos lógicos de requisição. No NS-3, a saturação aparece como perda de pacotes e atraso, pois os fluxos UDP continuam injetando tráfego.

## 4. Versão atual válida

A versão atual válida da frente NS-3 é:

```text
dynamic_v3
```

Arquivo principal utilizado:

```text
~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

Essa versão inclui:

- 19 beams;
- 48 canais totais;
- máximo de 6 canais por beam;
- mínimo de 1 canal por beam ativo;
- capacidade de 1.1 Mbps por canal;
- controle de alocação a cada 1 segundo;
- backlog virtual em nível IP;
- cálculo de satisfação de demanda;
- cálculo de backlog médio e máximo;
- cálculo de métricas globais e por beam;
- políticas `equal`, `round_robin`, `longest_queue_first`, `greedy_backlog` e `proportional_fair`.

## 5. Sistema utilizado

Ambiente de referência:

```text
Ubuntu 24.04.3 LTS
VS Code
Python 3.12
NS-3.47
```

## 6. Dependências do sistema

Pacotes recomendados:

```bash
sudo apt update

sudo apt install -y \
  build-essential \
  gcc \
  g++ \
  python3 \
  python3-venv \
  python3-pip \
  cmake \
  ninja-build \
  git \
  wget \
  bzip2 \
  pkg-config \
  sqlite3 \
  libsqlite3-dev \
  libxml2 \
  libxml2-dev \
  libgsl-dev
```

Observação: alguns módulos opcionais do NS-3 podem aparecer como não compilados, como `ai`, `brite`, `click`, `openflow`, `visualizer` ou `quantum`. Para esta frente, isso não impede a execução, pois a simulação atual usa principalmente `core`, `network`, `internet`, `applications`, `point-to-point` e `flow-monitor`.

## 7. Instalação do NS-3

Caso seja necessário reinstalar:

```bash
mkdir -p ~/simulators
cd ~/simulators

wget https://www.nsnam.org/releases/ns-allinone-3.47.tar.bz2
tar xjf ns-allinone-3.47.tar.bz2

cd ns-allinone-3.47/ns-3.47

./ns3 configure --enable-examples --enable-tests
./ns3 build
./test.py
```

## 8. Estrutura da infraestrutura Python

A infraestrutura da frente NS-3 fica fora da pasta do NS-3:

```text
~/tcc-leo-ns3/
├── scripts/
│   ├── run_dynamic_v3_campaign.py
│   ├── collect_dynamic_v3_results.py
│   ├── plot_dynamic_v3_results.py
│   ├── make_dynamic_v3_tables.py
│   └── plot_dynamic_v3_publication.py
├── results/
│   └── dynamic_v3_campaign/
│       ├── light/
│       ├── medium/
│       └── heavy_controlled/
├── analysis/
│   └── dynamic_v3_campaign/
│       ├── summary_by_policy.csv
│       ├── beam_results.csv
│       ├── scenario_rankings.csv
│       ├── tables/
│       ├── figures/
│       └── figures_publication/
└── docs/
    ├── README_NS3_DYNAMIC_V3.md
    ├── NS3_RESULTS_INTERPRETATION.md
    └── NS3_PYTHON_ALIGNMENT.md
```

## 9. Ambiente Python da infraestrutura

Criar ambiente:

```bash
cd ~/tcc-leo-ns3

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install pandas matplotlib tabulate
```

Observação: `tabulate` é usado para exportar tabelas Markdown com `pandas.to_markdown()`.

## 10. Rodar campanha principal

A campanha principal usa três cenários:

| Cenário | baseUserRateMbps | hotspotUserRateMbps | Papel |
|---|---:|---:|---|
| light | 0.3 | 1.0 | carga leve |
| medium | 0.5 | 2.0 | cenário principal |
| heavy_controlled | 0.6 | 2.5 | carga pesada controlada |

Executar:

```bash
cd ~/tcc-leo-ns3
source .venv/bin/activate

python scripts/run_dynamic_v3_campaign.py --build
```

Resultados:

```text
~/tcc-leo-ns3/results/dynamic_v3_campaign/
```

## 11. Rodar cenário extremo

O cenário extremo é apenas teste de limite, não cenário principal.

```bash
cd ~/tcc-leo-ns3
source .venv/bin/activate

python scripts/run_dynamic_v3_campaign.py --scenarios extreme --include-extreme
```

Parâmetros do cenário extremo:

| Cenário | baseUserRateMbps | hotspotUserRateMbps | Papel |
|---|---:|---:|---|
| extreme | 0.8 | 3.0 | teste de limite |

## 12. Consolidar resultados

Após rodar a campanha:

```bash
cd ~/tcc-leo-ns3
source .venv/bin/activate

python scripts/collect_dynamic_v3_results.py
```

Arquivos gerados:

```text
analysis/dynamic_v3_campaign/summary_by_policy.csv
analysis/dynamic_v3_campaign/beam_results.csv
analysis/dynamic_v3_campaign/scenario_rankings.csv
```

## 13. Gerar gráficos diagnósticos

```bash
python scripts/plot_dynamic_v3_results.py
```

Saída:

```text
analysis/dynamic_v3_campaign/figures/
```

Esses gráficos são úteis para inspeção e depuração.

## 14. Gerar tabelas revisadas

```bash
python scripts/make_dynamic_v3_tables.py
```

Saída:

```text
analysis/dynamic_v3_campaign/tables/
├── tabela_resumo_metricas.csv
├── tabela_resumo_metricas.md
├── tabela_resumo_metricas.tex
├── tabela_ranking_cenarios.csv
├── tabela_ranking_cenarios.md
└── tabela_ranking_cenarios.tex
```

Essas tabelas são as mais indicadas para uso no TCC.

## 15. Gerar gráficos revisados para relatório

```bash
python scripts/plot_dynamic_v3_publication.py
```

Saída:

```text
analysis/dynamic_v3_campaign/figures_publication/
```

Esses gráficos são os mais indicados para apresentação e escrita do TCC.

## 16. Arquivos atualmente utilizados

### Código NS-3 utilizado

```text
~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

### Scripts Python utilizados

```text
~/tcc-leo-ns3/scripts/run_dynamic_v3_campaign.py
~/tcc-leo-ns3/scripts/collect_dynamic_v3_results.py
~/tcc-leo-ns3/scripts/plot_dynamic_v3_results.py
~/tcc-leo-ns3/scripts/make_dynamic_v3_tables.py
~/tcc-leo-ns3/scripts/plot_dynamic_v3_publication.py
```

### Resultados principais utilizados

```text
~/tcc-leo-ns3/results/dynamic_v3_campaign/
```

### Análises principais utilizadas

```text
~/tcc-leo-ns3/analysis/dynamic_v3_campaign/
```

## 17. Arquivos e pastas deprecated

Os seguintes arquivos/pastas foram úteis no desenvolvimento, mas não devem ser usados como resultado principal:

```text
~/tcc-leo-ns3/results/basic_fixed/
~/tcc-leo-ns3/results/basic_agg/
~/tcc-leo-ns3/results/dynamic_v1/
~/tcc-leo-ns3/results/dynamic_v1_capacity_1_1/
~/tcc-leo-ns3/results/dynamic_v2/
~/tcc-leo-ns3/results/dynamic_v3/
~/tcc-leo-ns3/results/dynamic_v3_stress/
```

Motivo:

- `basic_fixed`: primeira validação, antes do modelo agregado final.
- `basic_agg`: validação agregada inicial, sem alocação dinâmica.
- `dynamic_v1`: versão inicial com artefatos de capacidade e overhead.
- `dynamic_v1_capacity_1_1`: corrigiu overhead, mas ainda sem estabilização final.
- `dynamic_v2`: melhorou starvation e métricas, mas ainda tinha ambiguidades entre políticas.
- `dynamic_v3`: execução manual do cenário médio; mantida como referência, mas substituída pela campanha automatizada.
- `dynamic_v3_stress`: cenário extremo, deve ser tratado como teste de limite.

Também são considerados obsoletos como versão principal:

```text
scratch/leo-multibeam-dynamic.v1.old.cc
scratch/leo-multibeam-dynamic.v2.old.cc
scratch/leo-multibeam-basic.cc
scratch/leo-multibeam-basic-agg.cc
```

Observação: os arquivos `basic` podem ser mantidos como histórico de validação, mas não devem ser usados como resultado principal do TCC.

## 18. Fluxo recomendado completo

```bash
cd ~/tcc-leo-ns3
source .venv/bin/activate

python scripts/run_dynamic_v3_campaign.py --build
python scripts/collect_dynamic_v3_results.py
python scripts/make_dynamic_v3_tables.py
python scripts/plot_dynamic_v3_publication.py
```

## 19. Métricas principais para análise

Usar como métricas principais:

- vazão total recebida;
- satisfação global de demanda;
- taxa global de perda;
- atraso médio global;
- backlog médio final;
- backlog máximo final;
- satisfação de demanda do hotspot;
- perda do hotspot;
- backlog final do hotspot.

Usar como métrica complementar:

- fairness de Jain sobre vazão.

## 20. Observação metodológica final

A frente NS-3 deve ser interpretada como validação complementar da frente Python. Ela não substitui o simulador Python e não deve ser usada para afirmar equivalência numérica direta.

A função da frente NS-3 é mostrar que, ao transformar a alocação dinâmica de canais em capacidade de enlace, os efeitos esperados aparecem em nível de rede: políticas adaptativas melhoram satisfação e reduzem backlog sob hotspot, enquanto políticas uniformes tendem a deixar o beam mais carregado subatendido.
