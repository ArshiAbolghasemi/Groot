# Groot Chatbot

A production-ready LangGraph chatbot with guardrails, Wikipedia search, streaming responses, parallel NER processing, and PostgreSQL persistence.

## Overview

Groot is an intelligent chatbot that:
- **Blocks political questions** using an LLM-based guardrail
- **Searches Wikipedia** for factual information
- **Streams responses** token-by-token for better UX
- **Extracts named entities** in parallel (PERSON, LOCATION, ORGANIZATION, DATE, OTHER)
- **Stores everything** in PostgreSQL with rich metadata

## Architecture

### High-Level Flow

```mermaid
graph TD
    A[User Question] --> B[START]
    B --> C[Parallel Start]
    C --> D[Guardrail]
    C --> E[NER]
    D --> F{Blocked?}
    F -->|Yes| G[Blocked Node]
    F -->|No| H[Agent]
    H --> I[Wikipedia Tool]
    I --> H
    H --> J[END]
    E --> J
    G --> J
    J --> K[Save to PostgreSQL]
    K --> L[Stream to User]
```

### Detailed Architecture

```mermaid
graph TB
    subgraph "User Interface"
        UI[CLI - main.py]
    end

    subgraph "Application Layer"
        SVC[ChatService]
    end

    subgraph "Orchestration Layer - LangGraph"
        START[START]
        PS[Parallel Start]
        GR[Guardrail Node]
        NER[NER Node]
        BLK[Blocked Node]
        AGT[Agent Node]
        END_NODE[END]

        START --> PS
        PS --> GR
        PS --> NER
        GR -->|blocked| BLK
        GR -->|allowed| AGT
        NER --> END_NODE
        AGT --> END_NODE
        BLK --> END_NODE
    end

    subgraph "Agent Internals - create_agent"
        MODEL[LLM Model]
        TOOLS[Wikipedia Tool]
        MODEL --> TOOLS
        TOOLS --> MODEL
    end

    subgraph "Infrastructure"
        LLM[OpenAI API]
        WIKI[Wikipedia API]
        DB[(PostgreSQL)]
    end

    UI --> SVC
    SVC --> START
    GR --> LLM
    NER --> LLM
    AGT --> MODEL
    MODEL --> LLM
    TOOLS --> WIKI
    END_NODE --> DB
    DB --> UI
```

### Parallel Execution

```mermaid
sequenceDiagram
    participant User
    participant Graph
    participant Guardrail
    participant NER
    participant Agent
    participant DB
 
    User->>Graph: "What is the capital of France?"
    Graph->>Guardrail: Check if political
    Graph->>NER: Extract entities

    par Parallel Execution
        Guardrail-->>Graph: ALLOWED (500ms)
    and
        NER-->>Graph: [{"entity": "France", "type": "LOCATION"}] (800ms)
    end

    Graph->>Agent: Process question
    Agent->>Agent: Call Wikipedia tool
    Agent-->>Graph: "The capital of France is Paris."
    Graph->>DB: Save (question + answer + entities)
    Graph-->>User: Stream response
```

## Key Features

### 1. Guardrail System

Blocks political questions before processing:

```mermaid
graph LR
    Q[Question] --> G[Guardrail LLM]
    G -->|0 BLOCKED| R[Refusal Message]
    G -->|1 ALLOWED| A[Agent Processing]
```

**Example:**
- Input: "Who should I vote for?"
- Output: "I'm sorry, I'm not able to discuss political topics."
- Database: `refusal=true`, entities extracted

### 2. Wikipedia Search Tool

Automatically searches Wikipedia when needed:

```mermaid
graph LR
    A[Agent] --> D{Need Info?}
    D -->|Yes| W[Wikipedia API]
    W --> R[Retry Logic]
    R --> A
    D -->|No| E[Generate Answer]
```

**Features:**
- Automatic retry with exponential backoff
- Configurable timeout (default: 30s)
- Returns top 5 results by default

### 3. Streaming Responses

Token-by-token streaming for better UX:

```mermaid
sequenceDiagram
    participant User
    participant Service
    participant Agent
    participant LLM

    User->>Service: Ask question
    Service->>Agent: Invoke
    Agent->>LLM: Stream request
    loop Token by token
        LLM-->>Agent: Token
        Agent-->>Service: Token
        Service-->>User: Display token
    end
```

### 4. Parallel NER Processing

Named Entity Recognition runs in parallel with guardrail:

```mermaid
graph TB
    START[Question] --> PS[Parallel Start]
    PS --> GR[Guardrail<br/>500ms]
    PS --> NER[NER<br/>800ms]
    GR --> NEXT[Next Step]
    NER --> NEXT

    style GR fill:#e1f5ff
    style NER fill:#e1f5ff
```

**Entity Types:**
- PERSON (e.g., "Albert Einstein")
- LOCATION (e.g., "France", "Paris")
- ORGANIZATION (e.g., "Microsoft", "NASA")
- DATE (e.g., "2024", "January")
- OTHER (anything else)

### 5. PostgreSQL Persistence

All interactions stored with rich metadata:

```mermaid
erDiagram
    CHAT_RECORDS {
        int id PK
        text question
        text answer
        boolean refusal
        json entities
        timestamp created_at
    }
```

**Example Record:**
```json
{
  "id": 1,
  "question": "What is the capital of France?",
  "answer": "The capital of France is Paris.",
  "refusal": false,
  "entities": [
    {"entity": "France", "type": "LOCATION"}
  ],
  "created_at": "2025-04-15T10:30:00Z"
}
```

## Installation

### Prerequisites

- Python 3.13+
- Docker (for PostgreSQL)
- OpenAI API key

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Groot
```

2. **Create virtual environment**
```bash
uv create venv
source .venv/bin/active
```

3. **Install dependencies**
```bash
uv sync
```

4. **Start PostgreSQL**
```bash
docker-compose up -d
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your configurations
```
