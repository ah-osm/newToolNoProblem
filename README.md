# newToolNoProblem 🎓

**An AI-powered multi-agent learning assistant that helps developers master emerging AI tools quickly and effectively.**

## 🎯 The Problem

In the fast-paced AI era, new tools and frameworks emerge constantly. Developers struggle to:
- Keep up with the rapid pace of new AI tools
- Find comprehensive, structured learning resources
- Create effective learning plans
- Track progress across multiple technologies
- Stay motivated while learning complex topics

## 💡 The Solution

**newToolNoProblem** is an intelligent multi-agent system that:
- Researches any AI tool comprehensively using Google Search
- Creates personalized, structured learning roadmaps
- Generates code examples and practice quizzes
- Tracks your progress and celebrates milestones
- **Saves everything locally** for offline access and token efficiency

## 🏗️ Architecture

The system uses a **Hub-and-Spoke Architecture** with **7 specialized AI agents** coordinated by a **Main Orchestrator Agent**.

### 🌟 Main Orchestrator Agent (The Hub)
The central intelligence that:
- **Orchestrates** the entire workflow
- **Manages Files**: Handles all file creation, reading, and saving (Centralized I/O)
- **Delegates Tasks**: Assigns work to specialist agents
- **Assembles Modules**: Combines content from multiple agents into final lessons

### 🤖 Specialist Agents (The Spokes)
Pure content generators that focus on their specific domains:

1.  **Researcher Agent** 🔍
    - Finds comprehensive information about AI tools
    - Synthesizes findings into clear summaries
2.  **Planner Agent** 📋
    - Creates detailed learning roadmaps
    - Defines prerequisites and learning paths
3.  **Teacher Agent** 👨‍🏫
    - Creates comprehensive, engaging lessons
    - Explains concepts with analogies and clarity
4.  **Example Agent** 💻
    - Generates well-commented code examples
    - Provides practical, real-world scenarios
5.  **Quiz Agent** 📝
    - Creates comprehensive quizzes with gradual difficulty
    - Tests understanding of the material
6.  **Tracker Agent** 📊
    - Monitors learning progress
    - Records milestones
7.  **Notifier Agent** 📢
    - Sends motivational messages and tips

### 🔄 Workflow: 

To ensure stability and compatibility with Google's ADK (Agent Development Kit), we use a **Centralized File Management** pattern:

1.  **User Request**: "I want to learn FastAPI"
2.  **Main Agent**:
    *   Creates folder `lessons/fastapi/`
    *   Calls **Researcher** -> gets content
    *   Saves content to `lessons/fastapi/research.md`
3.  **User Request**: "Start Module 1"
4.  **Main Agent**:
    *   Reads `research.md` & `roadmap.md`
    *   Passes context to **Teacher**, **Example**, and **Quiz** agents
    *   Receives content from all three
    *   **Assembles** into `lessons/fastapi/module_1.md`
    *   Returns the absolute path to the user

## 🛠️ Technical Implementation

**Key Features (Meeting course requirements):**

✅ **Multi-Agent System**
- 8 LLM-powered agents working in coordination
- **Agent-as-Tool Pattern**: Sub-agents are wrapped as `AgentTool` for the Main Agent

✅ **Tools**
- **Built-in**: `google_search`, `load_memory`
- **Custom (FunctionTool)**:
    - `create_tool_folder`: Manages directory structures
    - `save_to_tool_folder`: Persists content to files
    - `read_from_tool_folder`: Retrieves context for agents
    - `assemble_module_file`: Combines lesson components
    - `track_progress`: JSON-based progress tracking

✅ **Sessions & Memory**
- `InMemorySessionService` for conversation state
- `InMemoryMemoryService` for long-term context
- Persistent progress tracking via JSON files

✅ **Observability**
- `LoggingPlugin` for comprehensive logging
- Detailed agent interaction traces
- Rich Markdown rendering in the console

## 🚀 Setup

### Prerequisites
- Python 3.10+
- Google API Key (for Gemini)

### Installation

1.  **Clone the repository** (or download the files)

2.  **Create virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

## 📖 Usage

### Starting the Assistant

```bash
source .venv/bin/activate
python3 main.py
```

### Example Interactions

**1. Start Learning:**
```
You: I want to learn LangChain
```
*System researches LangChain, creates a folder, and saves a roadmap.*

**2. Generate a Module:**
```
You: Start module 1
```
*System reads the research, generates a lesson, examples, and a quiz, then saves it to `lessons/langchain/module_1.md`.*

**3. Check Progress:**
```
You: What's my progress?
```

**4. Get Help:**
```
You: help
```

## 📁 Project Structure

```
newToolNoProblem/
├── main.py              # All agents + orchestration logic
├── requirements.txt     # Dependencies
├── .env                 # API Key (ignored by git)
├── README.md            # Documentation
├── lessons/             # Generated learning content
│   └── [tool_name]/     # Tool-specific folders
│       ├── research.md
│       ├── roadmap.md
│       └── module_1.md
├── progress_*.json      # User progress data
└── session_*.json       # Session state
```

## 👥 Use Cases

- **New Framework Launch**: Stay ahead when new AI frameworks emerge
- **Career Development**: Systematically learn tools for job requirements
- **Team Onboarding**: Standardize learning for team members
- **Continuous Learning**: Track progress across multiple technologies

## 📝 License

This project was created for the Kaggle Agents Intensive Course Capstone 2025.

---

**Built with ❤️ using Google Agent Development Kit (ADK) and Gemini**
