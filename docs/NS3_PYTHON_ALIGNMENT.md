# Alinhamento entre a Frente Python e a Frente NS-3

## 1. Objetivo do alinhamento

Este documento explica como a frente NS-3 se relaciona com a frente Python do TCC.

A frente Python é o ambiente principal de modelagem, decisão, heurísticas e aprendizado por reforço. A frente NS-3 é uma frente complementar, usada para observar os efeitos da alocação dinâmica de canais em nível de rede.

## 2. Papel da frente Python

A frente Python modela o problema de forma abstrata e controlada.

Ela inclui:

- múltiplos beams;
- tráfego variável;
- hotspot;
- interferência simplificada;
- filas por beam;
- bloqueio por fila máxima;
- descarte por timeout;
- heurísticas de alocação;
- agente PPO;
- métricas de goodput, bloqueio, aceitação, atraso, utilização e fairness.

Essa frente é adequada para estudar a lógica de decisão e comparar estratégias de alocação em um ambiente controlado.

## 3. Papel da frente NS-3

A frente NS-3 modela os efeitos da alocação em nível de rede.

Ela inclui:

- beams como fluxos agregados;
- enlaces ponto-a-ponto com capacidade dinâmica;
- tráfego UDP;
- medição de vazão recebida;
- perda de pacotes;
- atraso médio;
- satisfação de demanda;
- backlog virtual;
- fairness sobre vazão.

Essa frente é adequada para verificar como as políticas se comportam quando a alocação de canais modifica a capacidade de enlaces simulados.

## 4. Comparação correta entre as frentes

A comparação entre Python e NS-3 deve ser feita por tendência, não por equivalência numérica direta.

Não se deve afirmar que:

```text
goodput_sum_mbps no Python é numericamente igual a total_rx_mbps no NS-3.
```

A formulação correta é:

```text
goodput_sum_mbps e total_rx_mbps representam, em níveis diferentes, a quantidade de tráfego efetivamente atendida.
```

## 5. Correspondência aproximada de métricas

| Python | NS-3 | Interpretação |
|---|---|---|
| `offered_load_mbps` | `total_offered_ip_mbps` | carga ofertada |
| `goodput_sum_mbps` | `total_rx_mbps` | tráfego efetivamente entregue |
| `served/offered` | `global_demand_satisfaction` | fração da demanda atendida |
| `blocking_rate` | `global_loss_rate` | degradação do atendimento, mas com naturezas diferentes |
| `queue/backlog` | `virtual_backlog_mb` | demanda acumulada não atendida |
| `delay/wait` | `mean_delay_ms` | custo temporal da saturação |
| `fairness` | `jain_fairness_rx_mbps` | justiça na distribuição |
| canais alocados | `allocated_channels` | decisão de recurso |

## 6. Diferença entre bloqueio e perda

No simulador Python, uma requisição pode ser bloqueada por fila máxima ou descartada por timeout.

No NS-3, os fluxos UDP continuam gerando pacotes. Quando a capacidade do enlace não é suficiente, a degradação aparece como perda de pacotes e aumento de atraso.

Portanto:

```text
blocking_rate no Python não é igual a loss_rate no NS-3.
```

Ambas indicam degradação, mas em níveis diferentes.

## 7. Sobre aprendizado por reforço

O aprendizado por reforço já foi explorado na frente Python com PPO.

Não é recomendado treinar um novo agente RL dentro do NS-3 nesta etapa do TCC, pois isso exigiria uma nova infraestrutura de co-simulação, definição de estado, ação, recompensa, episódios e integração com Python.

A frente NS-3 deve permanecer como validação complementar das políticas de alocação.

Como trabalho futuro, seria possível exportar decisões do agente PPO treinado no Python e aplicá-las no NS-3 como trace de alocação, ou criar uma interface de co-simulação para treinar agentes diretamente com métricas de rede.

## 8. Narrativa recomendada para o TCC

A narrativa metodológica recomendada é:

> O simulador Python foi utilizado como ambiente principal de investigação do problema de alocação dinâmica de canais, incluindo heurísticas e aprendizado por reforço. A frente NS-3 foi desenvolvida como verificação complementar, permitindo observar como políticas de alocação se manifestam em métricas de rede, como vazão, perda, atraso e backlog virtual. As frentes não são equivalentes em granularidade, mas são complementares para analisar o mesmo problema.

## 9. Conclusão do alinhamento

As duas frentes estão alinhadas ao mesmo problema central: a redistribuição dinâmica de canais em ambiente LEO multifeixe sob carga variável.

A frente Python é mais adequada para avaliar decisão e aprendizado. A frente NS-3 é mais adequada para observar efeitos de rede.

Assim, os resultados devem ser analisados conjuntamente por tendência, reforçando a conclusão de que políticas adaptativas são mais adequadas do que políticas uniformes em cenários com hotspot de tráfego.
