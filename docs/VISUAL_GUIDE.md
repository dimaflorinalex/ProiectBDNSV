# Visual Guide: Closed Feedback Loop System

## System Architecture

### Mermaid Diagram

```mermaid
graph TB
    subgraph UI["USER INTERFACES"]
        CLI["CLI Interface<br/>- Rate queries<br/>- Provide comments<br/>- Submit corrections<br/>- View learning"]
        WEB["Web Interface<br/>- Rating slider<br/>- Comment field<br/>- Correction input<br/>- Learning tab"]
    end
    
    subgraph FB["FEEDBACK COLLECTION"]
        FBH["FeedbackHandler<br/>- add_feedback()<br/>- add_correction()<br/>- get_positive_examples()<br/>- get_similar_queries()<br/>- get_corrected_examples()"]
    end
    
    subgraph DB["PERSISTENT STORAGE"]
        SQLDB["SQLite Database<br/>data/feedback.db<br/><br/>feedback table<br/>corrections table"]
    end
    
    subgraph LS["LEARNING SYSTEM"]
        FLS["FeedbackLearningSystem<br/>1. Analyze feedback<br/>2. Extract examples<br/>3. Find similar queries<br/>4. Retrieve corrections<br/>5. Build enhanced prompts"]
    end
    
    subgraph QG["QUERY GENERATION"]
        GEN["QueryGenerator<br/>Base Prompt +<br/>Learned Examples +<br/>Correction Guidance<br/>↓<br/>Enhanced Prompt → LLM"]
    end
    
    subgraph EX["EXECUTION"]
        EXEC["Execute SQL<br/>Get Results<br/>Summarize"]
    end
    
    CLI --> FBH
    WEB --> FBH
    FBH --> SQLDB
    SQLDB --> FLS
    FLS --> GEN
    GEN --> EXEC
    EXEC -.Loop back.-> UI
    
    style UI fill:#e1f5ff
    style FB fill:#fff3e0
    style DB fill:#f3e5f5
    style LS fill:#e8f5e9
    style QG fill:#fff9c4
    style EX fill:#fce4ec
```

### Text Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                        │
│  ┌───────────────────────┐         ┌─────────────────────┐  │
│  │   CLI Interface       │         │   Web Interface     │  │
│  │  - Rate queries       │         │  - Rating slider    │  │
│  │  - Provide comments   │         │  - Comment field    │  │
│  │  - Submit corrections │         │  - Correction input │  │
│  │  - View learning      │         │  - Learning tab     │  │
│  └──────────┬────────────┘         └──────────┬──────────┘  │
└─────────────┼────────────────────────────────┼──────────────┘
              │                                │
              └────────────────┬───────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                   FEEDBACK COLLECTION                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           FeedbackHandler                                │  │
│  │  - add_feedback(question, query, rating, comment)        │  │
│  │  - add_correction(feedback_id, original, corrected)      │  │
│  │  - get_positive_examples()                               │  │
│  │  - get_similar_queries(question)                         │  │
│  │  - get_corrected_examples()                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬─────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                    PERSISTENT STORAGE                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           SQLite Database (data/feedback.db)             │  │
│  │                                                          │  │
│  │  feedback table:                                         │  │
│  │    - question, sql_query, rating, comment, timestamp     │  │
│  │                                                          │  │
│  │  corrections table:                                      │  │
│  │    - feedback_id, original_query, corrected_query        │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬─────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LEARNING SYSTEM                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        FeedbackLearningSystem                            │   │
│  │                                                          │   │
│  │  1. Analyze stored feedback                              │   │
│  │  2. Extract positive examples (rating ≥ 4)               │   │
│  │  3. Find similar queries (keyword matching)              │   │
│  │  4. Retrieve user corrections                            │   │
│  │  5. Build enhanced prompts                               │   │
│  │                                                          │   │
│  │  Methods:                                                │   │
│  │  - build_learned_examples(question)                      │   │
│  │  - build_correction_guidance()                           │   │
│  │  - enhance_prompt_with_feedback(prompt, question)        │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   QUERY GENERATION                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           QueryGenerator                                 │   │
│  │                                                          │   │
│  │  Base Prompt                                             │   │
│  │       +                                                  │   │
│  │  Learned Examples (if available)                         │   │
│  │       +                                                  │   │
│  │  Correction Guidance (if available)                      │   │
│  │       ↓                                                  │   │
│  │  Enhanced Prompt → LLM → Better SQL Query                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      EXECUTION                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Execute SQL → Get Results → Summarize                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
                    Present to User (loop back)
```

## Data Flow: User Feedback to Improved Queries

### Mermaid Diagram

```mermaid
sequenceDiagram
    actor User
    participant System
    participant DB as Database
    participant Learning as Learning System
    
    Note over User,System: Step 1: User Interaction
    User->>System: "How many employees?"
    System->>User: SELECT COUNT(*) FROM employees
    User->>System: ⭐⭐⭐⭐⭐ (5 stars) "Perfect!"
    
    Note over System,DB: Step 2: Storage
    System->>DB: Store feedback<br/>question, query, rating=5
    
    Note over User,Learning: Step 3: Next Query (Learning)
    User->>System: "How many departments?"
    System->>Learning: Find similar queries
    Learning->>DB: Get examples with "how many"
    DB->>Learning: Return COUNT(*) examples
    Learning->>System: Enhanced prompt with examples
    
    Note over System,User: Step 4: Better Result
    System->>User: SELECT COUNT(*) FROM departments<br/>✅ Correct (learned from example)
```

### Text Diagram

```
Step 1: User Interaction
┌───────────────────────────────────────────┐
│ User: "How many employees are there?"     │
│ System: "SELECT COUNT(*) FROM employees"  │
│ User: ⭐⭐⭐⭐⭐ (5 stars) "Perfect!"   │
└───────────────────────────────────────────┘
                    ↓
Step 2: Storage
┌─────────────────────────────────────────┐
│ Saved to database:                      │
│ - question: "How many employees..."     │
│ - query: "SELECT COUNT(*)..."           │
│ - rating: 5                             │
│ - comment: "Perfect!"                   │
└─────────────────────────────────────────┘
                    ↓
Step 3: Learning (Next Query)
┌─────────────────────────────────────────┐
│ User asks: "How many departments?"      │
│                                         │
│ System finds similar query:             │
│ ✓ Keywords: "how many" (similar)        │
│ ✓ Previous: COUNT(*) worked well        │
│                                         │
│ Enhanced prompt includes:               │
│ "Example: Q: How many employees?        │
│          A: SELECT COUNT(*) FROM..."    │
└─────────────────────────────────────────┘
                    ↓
Step 4: Better Result
┌─────────────────────────────────────────┐
│ Generated: "SELECT COUNT(*) FROM        │
│             departments"                │
│                                         │
│ ✅ Correct syntax (learned from example)│
│ ✅ Higher success rate                  │
└─────────────────────────────────────────┘
```

## Correction Flow

### Mermaid Diagram

```mermaid
flowchart TD
    A[User Question:<br/>Average salary?] --> B[System Generates:<br/>SELECT AVG salary emp]
    B --> C{Execute Query}
    C -->|Syntax Error| D[❌ Error Result]
    D --> E[User rates: ⭐ 1 star]
    E --> F[User provides correction:<br/>SELECT AVG salary<br/>FROM employees]
    F --> G[Store correction in DB]
    G --> H[Next similar query]
    H --> I[Enhanced prompt includes:<br/>Common mistake:<br/>Wrong: SELECT AVG salary emp<br/>Right: SELECT AVG salary FROM emp]
    I --> J[✅ Generate correct query]
    
    style D fill:#ffcdd2
    style E fill:#ffcdd2
    style F fill:#fff9c4
    style G fill:#c8e6c9
    style J fill:#c8e6c9
```

### Text Diagram

```
User provides wrong query correction:

Before:
┌─────────────────────────────────────────┐
│ Question: "Average salary?"             │
│ Generated: "SELECT AVG(salary) emp"     │
│ Result: ❌ Syntax Error                 │
│ Rating: ⭐ (1 star)                     │
└─────────────────────────────────────────┘
                    ↓
User corrects:
┌─────────────────────────────────────────┐
│ Corrected: "SELECT AVG(salary)          │
│             FROM employees"             │
│                                         │
│ System stores correction                │
└─────────────────────────────────────────┘
                    ↓
Next similar query:
┌────────────────────────────────────────┐
│ Prompt includes:                       │
│ "Common mistake to avoid:              │
│  Wrong: SELECT AVG(salary) emp         │
│  Right: SELECT AVG(salary) FROM emp"   │
│                                        │
│ Result: ✅ Correct query generated    │
└────────────────────────────────────────┘
```

## Learning Activation Logic

### Mermaid Diagram

```mermaid
flowchart TD
    Start([Query Comes In]) --> Check{Check has_learning_data}
    Check -->|Has Data| Enhance[Enhance Prompt with Feedback]
    Check -->|No Data| Standard[Use Standard Prompt]
    
    Enhance --> Generate[Generate Query]
    Standard --> Generate
    
    subgraph "has_learning_data() Logic"
        direction TB
        H1[Check positive examples<br/>rating >= 4] --> H2{Count >= 3?}
        H2 -->|Yes| Return1[Return True]
        H2 -->|No| H3[Check corrections<br/>rating <= 2 AND corrected]
        H3 --> H4{Count >= 1?}
        H4 -->|Yes| Return2[Return True]
        H4 -->|No| Return3[Return False]
    end
    
    Check -.-> H1
    
    style Return1 fill:#c8e6c9
    style Return2 fill:#c8e6c9
    style Return3 fill:#ffcdd2
    style Enhance fill:#bbdefb
    style Standard fill:#f5f5f5
```

### Text Diagram

```
┌─────────────────────────────────────────┐
│ Check: has_learning_data()              │
└─────────────────────────────────────────┘
                    ↓
         ┌──────────┴──────────┐
         ↓                     ↓
┌──────────────────┐  ┌──────────────────┐
│ Positive examples│  │   Corrections    │
│   (rating ≥ 4)   │  │  (any number)    │
└──────────────────┘  └──────────────────┘
         ↓                     ↓
    Count ≥ 3?            Count ≥ 1?
         ↓                     ↓
         └──────────┬──────────┘
                    ↓
              YES or YES?
                    ↓
              ┌─────────┐
              │ ENABLE  │
              │LEARNING │
              └─────────┘
                    ↓
        Use feedback in prompts
```

## UI Components

### Mermaid Diagram - CLI Flow

```mermaid
flowchart LR
    A[User Query Input] --> B[Generate SQL]
    B --> C[Execute Query]
    C --> D[Display Results]
    D --> E{Rating Prompt}
    E -->|⭐ 1-2| F[Correction Input:<br/>Enter correct SQL]
    E -->|⭐ 3-5| G[Thanks!]
    F --> H[(Store Correction)]
    G --> I[(Store Rating)]
    
    style F fill:#fff9c4
    style H fill:#c8e6c9
    style I fill:#c8e6c9
```

### Mermaid Diagram - Web Interface Layout

```mermaid
graph TB
    subgraph "Query Tab"
        W1[Question Input]
        W2[Generate Button]
        W3[Results Display]
        W4[Rating 1-5 ⭐]
        W5[Correction Input<br/>If rating ≤ 2]
        W6[Submit Feedback Button]
        
        W1 --> W2 --> W3
        W3 --> W4 --> W5 --> W6
    end
    
    subgraph "Learning System Tab"
        L1[Status Display:<br/>✅ Active / ⚠️ Inactive]
        L2[Positive Examples: X]
        L3[Corrections: Y]
        L4[Recent Improvements List]
        L5[Refresh Button]
        
        L1 --- L2 --- L3 --- L4 --- L5
    end
    
    style W5 fill:#fff9c4
    style L1 fill:#bbdefb
    style L4 fill:#c8e6c9
```

### Text Mockups

### CLI Commands:
```
┌─────────────────────────────────────────────────┐
│ TEXT-TO-SQL APPLICATION                         │
├─────────────────────────────────────────────────┤
│ Commands:                                       │
│ • Type question      → Generate SQL             │
│ • compare           → Compare LLMs              │
│ • stats             → Feedback statistics       │
│ • learning          → Learning system status    │
│ • quit/exit         → Exit                      │
├─────────────────────────────────────────────────┤
│ 💭 Your question: _                             │
└─────────────────────────────────────────────────┘
```

### Web Interface Tabs:
```
┌───────────────────────────────────────────────────────┐
│ [Query Generator] [Model Comparison] [Statistics]     │
│ [Learning System] [About]                             │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Your Question: [________________]                    │
│                                                       │
│  ☐ Use Few-Shot   ☐ Use Chain-of-Thought             │
│                                                       │
│  [Generate SQL]                                       │
│                                                       │
│  Generated SQL: SELECT COUNT(*) FROM employees        │
│                                                       │
│  Results: [table with data]                           │
│                                                       │
│  Rating: [1----3----5]                                │
│  Comment: [____]                                      │
│  Correction (optional): [____]                        │
│                                                       │
│  [Submit Feedback]                                    │
└───────────────────────────────────────────────────────┘
```

## Metrics Dashboard

```
┌─────────────────────────────────────────────────┐
│           LEARNING SYSTEM STATUS                │
├─────────────────────────────────────────────────┤
│ Learning Data Available:  ✅ Yes                │
│ Positive Examples:        12                    │
│ Corrections:              3                     │
│ Total Feedback:           18                    │
│ Average Rating:           4.2/5 ⭐⭐⭐⭐      │
├─────────────────────────────────────────────────┤
│ IMPROVEMENT SUGGESTIONS:                        │
│ • Feedback system working well!                 │
│ • Continue providing feedback                   │
└─────────────────────────────────────────────────┘
```

## Key Success Indicators

### System is Learning When:
✅ Positive examples > 0
✅ Similar queries return faster/better results
✅ Average rating increases over time
✅ Fewer syntax errors
✅ Corrections reduce repeated mistakes

### System Needs More Data When:
⚠️ Positive examples < 3
⚠️ No corrections recorded
⚠️ Average rating < 3.5
⚠️ Total feedback < 10
