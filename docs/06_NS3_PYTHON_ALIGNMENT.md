# Alinhamento entre a Frente Python e a Frente NS-3

## 1. Objetivo do alinhamento

Este documento explica como a frente NS-3 se relaciona com a frente Python do TCC. As duas frentes estudam o mesmo problema central: alocação dinâmica de canais em ambiente LEO multifeixe sob carga variável. Porém, elas fazem isso em níveis diferentes de abstração.

A frente Python é o ambiente principal de decisão, heurísticas, filas, bloqueio, timeout e aprendizado por reforço. A frente NS-3 é uma verificação complementar em nível de rede, observando vazão, perda, atraso, backlog virtual e satisfação de demanda.

## 2. Papel da frente Python

A frente Python modela o problema de forma lógica e controlada. Ela permite variar carga, interferência e congestionamento; comparar heurísticas; treinar e avaliar PPO; e medir goodput, bloqueio, aceitação, serviço, atraso, fila e fairness.

## 3. Papel da frente NS-3

A frente NS-3 observa o efeito da alocação em nível de rede. Ela permite transformar canais alocados em capacidade de enlace, observar vazão recebida, medir perda de pacotes, medir atraso médio, calcular satisfação de demanda e acompanhar backlog virtual.

## 4. Correspondência aproximada de métricas

| Frente Python     | Frente NS-3                                  | Interpretação                                         |
|:------------------|:---------------------------------------------|:------------------------------------------------------|
| offered_load_mbps | total_offered_ip_mbps                        | Carga ofertada                                        |
| goodput_sum_mbps  | total_rx_mbps                                | Tráfego efetivamente entregue                         |
| served/offered    | global_demand_satisfaction                   | Fração da demanda atendida                            |
| blocking_rate     | global_loss_rate                             | Degradação do atendimento, mas com natureza diferente |
| fila/backlog      | virtual_backlog_mb                           | Demanda acumulada não atendida                        |
| delay/wait        | mean_delay_ms                                | Custo temporal da saturação                           |
| fairness          | jain_fairness_rx_mbps                        | Justiça na distribuição de vazão                      |
| canais alocados   | allocated_channels / last_allocated_channels | Decisão de recurso por beam                           |
| PPO               | não implementado na frente NS-3              | RL permanece como contribuição da frente Python       |

## 5. Comparação correta entre as frentes

A comparação correta deve ser feita por tendência, e não por igualdade numérica direta.

Não se deve afirmar que:

```text
goodput_sum_mbps no Python é numericamente igual a total_rx_mbps no NS-3.
```

A formulação correta é:

```text
goodput_sum_mbps e total_rx_mbps representam, em níveis diferentes, a quantidade de tráfego efetivamente atendida.
```

## 6. Diferença entre bloqueio e perda

No Python, `blocking_rate` representa rejeição lógica ou descarte por mecanismos como fila máxima e timeout. No NS-3, `global_loss_rate` representa perda em nível de pacote, resultante da saturação dos enlaces e das filas de rede.

## 7. Sobre RL no NS-3

Não é recomendado treinar RL diretamente no NS-3 nesta etapa do TCC. Como o PPO já foi implementado e avaliado na frente Python, a contribuição de RL já está coberta. O NS-3 deve permanecer como frente complementar de validação em rede.

## 8. Possibilidade futura

Como trabalho futuro, seria possível exportar ações do agente PPO treinado em Python, aplicá-las no NS-3 como trace de alocação e comparar o impacto da política aprendida em vazão, perda e atraso de rede.

## 9. Narrativa recomendada para o TCC

> A frente Python foi utilizada como ambiente principal de investigação da alocação dinâmica de canais, incluindo heurísticas e aprendizado por reforço. A frente NS-3 foi desenvolvida como verificação complementar em nível de rede. Os resultados das duas frentes não são numericamente equivalentes, mas são metodologicamente complementares: a primeira avalia decisão e controle em ambiente abstrato; a segunda observa efeitos de rede como vazão, perda, atraso e backlog virtual.

## 10. Conclusão do alinhamento

As duas frentes estão alinhadas ao mesmo problema, mas em granularidades distintas. A frente Python sustenta a contribuição de IA e decisão. A frente NS-3 sustenta a verificação complementar de rede.
