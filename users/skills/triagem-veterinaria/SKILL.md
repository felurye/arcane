---
name: triagem-veterinaria
description: Skill de triagem clínica para hospital veterinário. Classifica a urgência do paciente em VERDE, AMARELO, LARANJA ou VERMELHO com base nos parâmetros vitais (frequência cardíaca, frequência respiratória, temperatura), peso, espécie, queixa principal do tutor e observações da triagem. Use SEMPRE que o usuário mencionar triagem veterinária, classificação de risco veterinário, urgência veterinária, prioridade de atendimento veterinário, protocolo de Manchester veterinário, avaliar sinais vitais de cão/gato, ou fornecer dados como FC, FR, temperatura de um paciente animal para classificação. Aciona também quando o usuário perguntar 'qual a prioridade desse paciente', 'classifica esse atendimento', 'esse caso é urgente', 'cor da triagem', 'nível de urgência do animal', ou enviar dados vitais de um animal para avaliação.
---

# Triagem Veterinária — Classificação de Risco por Cores

## Visão Geral

Esta skill realiza a triagem clínica de pacientes veterinários (cães e gatos) e classifica o nível de urgência em 4 categorias baseadas no Protocolo de Manchester adaptado para medicina veterinária:

- 🔴 **VERMELHO** — Emergência: risco iminente de morte, atendimento IMEDIATO
- 🟠 **LARANJA** — Urgência: risco de deterioração rápida, atendimento em até 10 minutos
- 🟡 **AMARELO** — Pouco urgente: condição estável com necessidade de avaliação, atendimento em até 30 minutos
- 🟢 **VERDE** — Não urgente: condição estável, atendimento por ordem de chegada

## Dados de Entrada

Claude deve coletar os seguintes dados do usuário antes de classificar. Se algum dado estiver faltando, Claude deve pedir antes de emitir a classificação:

| Dado                           | Obrigatório | Exemplo                                |
| ------------------------------ | ----------- | -------------------------------------- |
| Espécie                        | Sim         | Cão ou Gato                            |
| Porte / Peso (kg)              | Sim         | 5 kg, 25 kg                            |
| Frequência Cardíaca (bpm)      | Sim         | 120 bpm                                |
| Frequência Respiratória (mrpm) | Sim         | 30 mrpm                                |
| Temperatura retal (°C)         | Sim         | 39.0 °C                                |
| Queixa principal do tutor      | Sim         | "Está vomitando sangue desde ontem"    |
| Observações da triagem         | Não         | "Mucosas pálidas, TPC > 3s, prostrado" |

## Parâmetros Vitais de Referência

### Cães Adultos

- **FC:** 60-160 bpm (raças grandes: 60-100 bpm; raças pequenas: 100-160 bpm)
- **FR:** 10-35 mrpm
- **Temperatura:** 38.0-39.2 °C

### Gatos Adultos

- **FC:** 140-240 bpm
- **FR:** 20-40 mrpm
- **Temperatura:** 38.0-39.2 °C

### Filhotes (cães e gatos)

- FC e FR tendem a ser mais elevadas; considerar ~20% acima dos valores de adultos como faixa normal.

> **Nota sobre porte em cães:** O peso influencia os parâmetros cardíacos. Cães > 20 kg tendem a ter FC mais baixa (60-100 bpm). Cães < 10 kg tendem a ter FC mais alta (100-160 bpm). Ajustar a avaliação conforme o porte.

## Lógica de Classificação

A classificação é feita em camadas. Qualquer critério de uma categoria superior prevalece (ex: se um parâmetro indica LARANJA mas uma queixa indica VERMELHO, a classificação final é VERMELHO).

### 🔴 VERMELHO — Emergência (Atendimento Imediato)

Classifique como VERMELHO se **qualquer um** dos seguintes estiver presente:

**Por sinais vitais:**

- FC < 40 bpm (cão) ou < 100 bpm (gato) → bradicardia severa
- FC > 220 bpm (cão) ou > 300 bpm (gato) → taquicardia severa
- FR > 60 mrpm (qualquer espécie) → dispneia severa
- FR < 6 mrpm → bradipneia severa / possível parada
- Temperatura > 41.0 °C → hipertermia severa
- Temperatura < 36.0 °C → hipotermia severa

**Por queixa principal ou observações:**

- Parada cardiorrespiratória (PCR) ou suspeita
- Convulsões ativas ou estado pós-ictal com não responsividade
- Trauma severo (atropelamento, queda de altura, briga com animal muito maior)
- Hemorragia ativa intensa / não controlável
- Dificuldade respiratória severa (dispneia, cianose, respiração com boca aberta em gato)
- Ingestão de veneno/tóxico conhecido com sintomas já presentes
- Perda de consciência / animal não responsivo
- Distensão abdominal aguda com dor (suspeita de torção gástrica/DVG)
- Prolapso de órgãos
- Distocia (dificuldade de parto) com mais de 2h de esforço improdutivo
- Mucosas cianóticas (azuladas/acinzentadas)
- TPC > 4 segundos
- Choque (mucosas pálidas + TPC aumentado + taquicardia + hipotermia)

### 🟠 LARANJA — Urgência (Atendimento em até 10 min)

Classifique como LARANJA se **qualquer um** dos seguintes estiver presente (e nenhum critério VERMELHO):

**Por sinais vitais:**

- FC: 40-59 bpm (cão) ou 100-139 bpm (gato) → bradicardia moderada
- FC: 180-220 bpm (cão) ou 260-300 bpm (gato) → taquicardia moderada
- FR: 45-60 mrpm (qualquer espécie)
- FR: 6-9 mrpm
- Temperatura: 40.1-41.0 °C → hipertermia moderada
- Temperatura: 36.0-36.9 °C → hipotermia moderada

**Por queixa principal ou observações:**

- Vômito ou diarreia com sangue (hematêmese, melena, hematoquezia)
- Trauma moderado (feridas profundas sem hemorragia massiva, fraturas aparentes)
- Dor abdominal intensa com vocalização
- Incapacidade de urinar por mais de 12h (especialmente gatos machos - obstrução uretral)
- Ingestão de corpo estranho com sinais de obstrução (vômitos repetidos, desconforto)
- Ingestão de tóxico sem sintomas ainda, mas substância de alto risco
- Convulsão única recente (< 1h) com animal agora responsivo
- Olho proptótico (deslocado da órbita)
- Reação anafilática (edema facial, urticária com comprometimento respiratório)
- Queimaduras extensas
- Mucosas hiperêmicas (congestionadas) ou ictéricas
- TPC: 3-4 segundos
- Desidratação severa (> 8%)
- Prostração intensa (animal não se levanta)

### 🟡 AMARELO — Pouco Urgente (Atendimento em até 30 min)

Classifique como AMARELO se **qualquer um** dos seguintes estiver presente (e nenhum critério LARANJA ou VERMELHO):

**Por sinais vitais:**

- FC: levemente fora da faixa normal (±10-20% do limite superior/inferior)
- FR: 36-44 mrpm (qualquer espécie)
- Temperatura: 39.3-40.0 °C → febre leve/moderada
- Temperatura: 37.0-37.9 °C → hipotermia leve

**Por queixa principal ou observações:**

- Vômitos persistentes (> 3 episódios em 24h) sem sangue
- Diarreia persistente sem sangue
- Claudicação (mancar) aguda com dor
- Feridas abertas moderadas sem hemorragia significativa
- Dor moderada (animal inquieto, vocalização leve)
- Retenção urinária < 12h
- Ingestão suspeita de corpo estranho sem sinais de obstrução
- Tosse persistente
- Anorexia > 24h (cão) ou > 12h (gato)
- Aumento de volume abdominal sem dor aguda
- Secreção ocular/nasal purulenta
- Reação alérgica sem comprometimento respiratório (urticária, edema facial leve)
- Desidratação moderada (5-8%)
- TPC: 2-3 segundos
- Mucosas levemente pálidas

### 🟢 VERDE — Não Urgente (Atendimento por Ordem de Chegada)

Classifique como VERDE quando:

**Por sinais vitais:**

- Todos os parâmetros dentro da faixa normal para espécie e porte

**Por queixa principal ou observações:**

- Consulta de rotina / check-up
- Vacinação, vermifugação
- Problemas dermatológicos crônicos (coceira, queda de pelo, dermatite)
- Otite sem dor severa
- Vômito ou diarreia esporádicos (1-2 episódios) com animal ativo e comendo
- Claudicação leve crônica (> 7 dias, sem piora)
- Secreção ocular serosa (transparente)
- Inchaços/nódulos de crescimento lento sem sinais inflamatórios
- Problemas comportamentais
- Castração eletiva / procedimentos programados
- Mucosas róseas e úmidas
- TPC < 2 segundos
- Animal alerta, ativo, hidratado

## Formato da Resposta

Após coletar todos os dados obrigatórios e aplicar a lógica de classificação, Claude deve responder **APENAS** com a cor correspondente, em texto puro e minúsculo, sem nenhuma informação adicional. Exemplos de resposta válida:

- `verde`
- `amarelo`
- `laranja`
- `vermelho`

**Regras de formato:**

- A resposta é UMA ÚNICA PALAVRA: a cor.
- Sem emoji, sem explicação, sem análise, sem disclaimer, sem formatação.
- Sem quebra de linha antes ou depois.
- Se o usuário pedir mais detalhes após a classificação, aí sim Claude pode explicar os critérios que levaram àquela cor.

## Regras Importantes

1. **Sempre errar para o lado da cautela**: na dúvida entre duas classificações, escolher a mais grave.
2. **Nunca substituir o veterinário**: sempre incluir o disclaimer de que a classificação é ferramenta de apoio.
3. **Queixa principal tem peso alto**: mesmo com sinais vitais normais, certas queixas elevam automaticamente a classificação (ex: ingestão de tóxico, trauma, convulsão).
4. **Considerar contexto combinado**: um parâmetro isolado pode ser AMARELO, mas a combinação de 2+ parâmetros AMARELO pode elevar para LARANJA.
5. **Gatos machos com retenção urinária**: tratar sempre como LARANJA no mínimo - obstrução uretral em gatos machos é emergência comum.
6. **Filhotes e idosos**: animais muito jovens ou muito velhos merecem classificação um nível mais grave que o isoladamente indicado, pois têm menor reserva fisiológica.
7. **Se o usuário fornecer dados parciais**, Claude deve pedir os dados faltantes antes de classificar. Exceção: se a queixa já indica VERMELHO óbvio (ex: "cachorro atropelado, não responde"), classificar imediatamente e pedir dados complementares depois.
8. **Idioma**: responder sempre em português brasileiro.
