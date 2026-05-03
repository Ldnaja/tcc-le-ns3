# Guia de Execução — Frente NS-3 do TCC LEO

Este documento explica como instalar, configurar, executar e analisar a frente NS-3 do TCC. O objetivo é tornar a execução reprodutível, desde a simulação `dynamic_v3` até a geração de tabelas e figuras revisadas.

## 1. Ambiente recomendado

- Ubuntu 24.04.3 LTS;
- NS-3.47;
- Python 3.12;
- VS Code;
- terminal Bash.

## 2. Dependências do sistema

```bash
sudo apt update
sudo apt install -y build-essential gcc g++ python3 python3-venv python3-pip cmake ninja-build git wget bzip2 pkg-config sqlite3 libsqlite3-dev libxml2 libxml2-dev libgsl-dev
```

## 3. Instalação do NS-3

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

## 4. Arquivo NS-3 esperado

```text
~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

Nesta revisão, o arquivo `leo-multibeam-dynamic.cc` foi enviado e validado como a versão `dynamic_v3`.

Para instalar o arquivo no NS-3, copie-o para o diretório `scratch`:

```bash
cp leo-multibeam-dynamic.cc ~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

Depois compile o NS-3:

```bash
cd ~/simulators/ns-allinone-3.47/ns-3.47
./ns3 build
```

Identificação do arquivo revisado:

```text
NS_LOG_COMPONENT_DEFINE("LeoMultibeamDynamicV3")
SHA-256: dbf2477b9c7b46065217318467a523e54996bdd1d7abb8f4071ee73c3eabb2cf
```

## 5. Ambiente Python

```bash
cd ~/tcc-leo-ns3
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pandas matplotlib tabulate
```

## 6. Verificação rápida

```bash
cd ~/tcc-leo-ns3
source .venv/bin/activate
python - <<'EOF'
import pandas as pd
import matplotlib
import tabulate
print('pandas ok:', pd.__version__)
print('matplotlib ok:', matplotlib.__version__)
print('tabulate ok')
EOF
```

## 7. Compilar NS-3

```bash
cd ~/simulators/ns-allinone-3.47/ns-3.47
./ns3 build
```

## 8. Rodar campanha principal

```bash
cd ~/tcc-leo-ns3
source .venv/bin/activate
python scripts/run_dynamic_v3_campaign.py --build
```

Saída principal:

```text
results/dynamic_v3_campaign/
├── light/
├── medium/
└── heavy_controlled/
```

## 9. Rodar cenário específico

```bash
python scripts/run_dynamic_v3_campaign.py --scenarios medium
```

```bash
python scripts/run_dynamic_v3_campaign.py --scenarios medium --policies proportional_fair
```

## 10. Rodar teste extremo

```bash
python scripts/run_dynamic_v3_campaign.py --scenarios extreme --include-extreme
```

O cenário extremo é teste de limite e não deve entrar como cenário principal.

## 11. Consolidar resultados

```bash
python scripts/collect_dynamic_v3_results.py
```

Arquivos gerados:

```text
analysis/dynamic_v3_campaign/summary_by_policy.csv
analysis/dynamic_v3_campaign/beam_results.csv
analysis/dynamic_v3_campaign/scenario_rankings.csv
```

## 12. Gerar tabelas revisadas

```bash
python scripts/make_dynamic_v3_tables.py
```

## 13. Gerar figuras revisadas

```bash
python scripts/plot_dynamic_v3_publication.py
```

## 14. Fluxo completo recomendado

```bash
cd ~/tcc-leo-ns3
source .venv/bin/activate
python scripts/run_dynamic_v3_campaign.py --build
python scripts/collect_dynamic_v3_results.py
python scripts/make_dynamic_v3_tables.py
python scripts/plot_dynamic_v3_publication.py
```

## 15. Diretórios principais

```text
results/dynamic_v3_campaign/
analysis/dynamic_v3_campaign/
analysis/dynamic_v3_campaign/tables/
analysis/dynamic_v3_campaign/figures_publication/
```

## 16. Pastas deprecated

Não usar como base principal: `basic_fixed`, `basic_agg`, `dynamic_v1`, `dynamic_v1_capacity_1_1`, `dynamic_v2`, `dynamic_v3`, `dynamic_v3_heavy_controlled` e `dynamic_v3_stress`.
