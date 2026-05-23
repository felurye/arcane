# PetCare - Sistema veterinário inteligente

O **PetCare** é o projeto construído ao longo do workshop Arcane. É um sistema de gestão veterinária com camada de IA integrada - não um CRUD genérico, mas uma aplicação real com agentes que raciocinam, consultam bases de conhecimento e agem sobre o mundo.

## Capabilities

### Triagem inteligente

O sistema conta com um agente de triagem veterinária que analisa os sintomas relatados pelo tutor e sugere um nível de urgência e possíveis hipóteses diagnósticas. O agente consulta uma base de conhecimento veterinário via RAG antes de responder, garantindo que as respostas sejam fundamentadas em informações específicas da clínica.

### RAG sobre base veterinária

O PetCare alimenta um vetor store com documentos veterinários (protocolos, fichas de anamnese, bulas, etc.). Quando um agente precisa responder sobre um caso clínico, ele busca semanticamente os trechos mais relevantes e os injeta como contexto no prompt - sem retreinar o modelo.

### Chat em tempo real com IA

Interface de chat integrada ao sistema, com comunicação via WebSockets (Django Channels). O assistente responde em tempo real e mantém o histórico da conversa, atuando como suporte para veterinários e atendentes durante a consulta.

### Secretária autônoma com Google Calendar

Agente com acesso a ferramentas externas: consulta disponibilidade, agenda consultas diretamente no Google Calendar e confirma com o tutor - tudo em linguagem natural, sem formulário.

### Citação de fontes

O sistema exibe as fontes do RAG usadas em cada resposta, permitindo rastrear de qual documento veio cada informação. Útil para auditoria e para aumentar a confiança do veterinário nas respostas do agente.

## Arquitetura geral

```
Django (back-end, ORM, autenticação)
    |
    +-- LangChain (orquestração de agentes e chains)
    |       |
    |       +-- Agente de triagem
    |       +-- Assistente de IA (chat)
    |       +-- Secretária autônoma (ferramentas externas)
    |
    +-- Vector Store (embeddings de documentos veterinários)
    |
    +-- Django Channels (WebSockets para chat em tempo real)
    |
    +-- Google Calendar API (agendamento autônomo)
```

## Modelos de dados principais

| Modelo        | Descrição                                                  |
| ------------- | ---------------------------------------------------------- |
| `Client`      | Tutor do animal (dados de contato)                         |
| `Patient`     | Animal (espécie, raça, histórico)                          |
| `Appointment` | Consulta agendada                                          |
| `Question`    | Pergunta feita ao assistente de IA                         |
| `RagContext`  | Chunks recuperados e usados como contexto em cada resposta |

## Cronograma do workshop

### Dia 1

- **Projeto PetCare** - apresentação do sistema que vamos construir
- **Teoria - Como funciona a criação de RAGs** - chunks, embeddings e recuperação semântica
- **Prática - Treinamento de agentes com base de dados real** - alimentar o vetor store com dados do PetCare
- **Prática - Config geral do projeto** - setup do Django + LangChain + variáveis de ambiente
- **Prática - Agente de triagem e resumo** - primeiro agente funcional
- **Prática - Assistente de IA** - chatbot integrado ao sistema

### Dia 2

- **Back-end - Chat em tempo real com IA** - WebSockets com Django Channels
- **Front-end - Chat em tempo real com IA** - interface de chat com JavaScript
- **Ver fontes** - como o agente cita as fontes do RAG
- **Secretária autônoma + Google Calendar** - agente com ferramentas externas e integração de calendário
- **Assistente de IA** - refinamento e testes finais
