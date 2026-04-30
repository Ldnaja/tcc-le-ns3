# Interpretação dos Resultados da Frente NS-3

## 1. Objetivo da análise

Esta análise consolida os resultados obtidos na frente NS-3 do TCC, cujo objetivo é verificar, em nível de rede, o comportamento de políticas de alocação dinâmica de canais em um ambiente LEO multifeixe simplificado.

A frente NS-3 não substitui o simulador Python. Ela atua como uma verificação complementar, observando como a redistribuição de canais impacta métricas como vazão, perda de pacotes, atraso, backlog virtual e satisfação de demanda.

## 2. Versão analisada

A versão consolidada é:

```text
dynamic_v3
```

Arquivo principal:

```text
~/simulators/ns-allinone-3.47/ns-3.47/scratch/leo-multibeam-dynamic.cc
```

Essa versão inclui:

- 19 beams;
- 48 canais totais;
- limite de 6 canais por beam;
- mínimo de 1 canal por beam ativo;
- capacidade de 1.1 Mbps por canal;
- controle de alocação a cada 1 segundo;
- backlog virtual calculado em nível IP;
- métricas globais e por beam;
- cenários leve, médio e pesado controlado;
- políticas `equal`, `round_robin`, `longest_queue_first`, `greedy_backlog` e `proportional_fair`.

## 3. Cenários utilizados

| Cenário | baseUserRateMbps | hotspotUserRateMbps | Papel experimental |
|---|---:|---:|---|
| `light` | 0.3 | 1.0 | Operação com folga |
| `medium` | 0.5 | 2.0 | Cenário principal |
| `heavy_controlled` | 0.6 | 2.5 | Carga pesada controlada |

A capacidade nominal total da rede é:

```text
48 canais × 1.1 Mbps = 52.8 Mbps
```

O cenário leve fica abaixo da capacidade total, o cenário médio introduz pressão localizada no hotspot, e o cenário pesado controlado fica levemente acima da capacidade nominal, permitindo observar saturação sem tornar o sistema completamente inviável.

## 4. Políticas avaliadas

### 4.1 Equal

Distribui canais de forma uniforme entre os beams ativos, sem considerar demanda ou backlog.

É usada como baseline simples.

### 4.2 Round Robin

Distribui canais de forma rotativa entre os beams ativos.

Também é uma baseline, mas com variação temporal na ordem de atendimento.

### 4.3 Longest Queue First

Prioriza beams com maior backlog virtual, alocando canais de forma moderada.

Na versão `dynamic_v3`, essa política reduz backlog sem concentrar recursos de forma destrutiva.

### 4.4 Greedy Backlog

Prioriza de forma agressiva os beams com maior pressão de backlog.

Apresenta boa vazão, mas pode gerar maior atraso, pois concentra recursos de maneira mais intensa.

### 4.5 Proportional Fair

Usa pressão de backlog e histórico de serviço para equilibrar atendimento e justiça.

É a política mais defensável como estratégia adaptativa balanceada.

## 5. Métricas principais

As métricas principais são:

- vazão total recebida;
- satisfação global de demanda;
- taxa global de perda;
- atraso médio global;
- backlog médio final;
- backlog máximo final;
- satisfação de demanda do hotspot;
- perda do hotspot;
- backlog final do hotspot.

A métrica de fairness de Jain é mantida como complementar, pois pode indicar equilíbrio de vazão mesmo quando o hotspot está subatendido.

## 6. Comportamento observado

### 6.1 Cenário leve

No cenário leve, as políticas adaptativas conseguem atender praticamente toda a demanda. Isso confirma que, quando há folga de capacidade, a alocação dinâmica consegue direcionar recursos ao hotspot sem prejudicar os demais beams.

As políticas `equal` e `round_robin` podem apresentar menor satisfação do hotspot, pois distribuem canais sem considerar a concentração de carga.

### 6.2 Cenário médio

No cenário médio, a pressão do hotspot fica mais clara. As políticas uniformes apresentam maior perda e maior backlog no hotspot, enquanto as políticas adaptativas reduzem o acúmulo de demanda e melhoram a satisfação global.

Esse cenário é o principal para análise do TCC, pois apresenta carga relevante sem entrar em colapso extremo.

### 6.3 Cenário pesado controlado

No cenário pesado controlado, a demanda total fica levemente acima da capacidade nominal da rede. Nesse caso, alguma perda é esperada.

As políticas `longest_queue_first` e `proportional_fair` apresentam melhor equilíbrio entre vazão, perda, atraso e backlog. A política `greedy_backlog` também alcança boa vazão, mas tende a gerar maior atraso, evidenciando o custo de uma alocação mais agressiva.

## 7. Interpretação geral

Os resultados indicam que políticas adaptativas são mais adequadas para cenários com hotspot de tráfego. Elas conseguem reduzir backlog e perda em comparação com políticas uniformes.

A política `equal` serve como referência mínima, mas sofre por não considerar demanda. A `round_robin` melhora em alguns casos, mas também não é orientada por carga. `Longest_queue_first` e `proportional_fair` apresentam os melhores resultados gerais. `Greedy_backlog` é útil para mostrar que priorizar agressivamente backlog pode melhorar vazão, mas com custo em atraso.

## 8. Conclusão da frente NS-3

A frente NS-3 confirma, em nível de rede, que a redistribuição dinâmica de canais é relevante para ambientes multifeixe com carga assimétrica.

O principal resultado é que políticas adaptativas melhoram a satisfação de demanda e reduzem backlog sob hotspot, enquanto políticas uniformes tendem a deixar o beam mais carregado subatendido.

Essa frente deve ser apresentada como validação complementar da frente Python, e não como substituição dela.
