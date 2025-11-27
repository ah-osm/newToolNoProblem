import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import AgentTool, google_search, load_memory, preload_memory, FunctionTool
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION - Change model version here
# =============================================================================
MODEL_NAME = "gemini-2.5-flash"  # You can change this to any Gemini model
# Available models: gemini-3-pro, gemini-2.5-flash,gemini-2.5-flash-lite, gemini-2.5-pro, gemini-1.5-pro, gemini-1.5-flash, etc.

# Configure Retry Options
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# =============================================================================
# CUSTOM TOOLS - Business Logic for Learning Management
# =============================================================================

def save_learning_roadmap(tool_name: str, roadmap: str) -> dict:
    """
    Saves a learning roadmap for a specific tool/technology to disk.
    
    Args:
        tool_name: Name of the tool (e.g., "LangChain", "FastAPI")
        roadmap: The complete learning roadmap as markdown text
        
    Returns:
        Dictionary with status and file path
    """
    try:
        filename = f"roadmap_{tool_name.lower().replace(' ', '_')}.md"
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'w') as f:
            f.write(f"# Learning Roadmap: {tool_name}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(roadmap)
        
        return {
            "status": "success",
            "message": f"Roadmap saved to {filename}",
            "filepath": filepath
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to save roadmap: {str(e)}"
        }


def create_practice_quiz(topic: str, difficulty: str = "beginner") -> dict:
    """
    Creates a structured practice quiz template for a given topic.
    
    Args:
        topic: The topic for the quiz (e.g., "LangChain basics")
        difficulty: Difficulty level (beginner, intermediate, advanced)
        
    Returns:
        Dictionary with quiz structure and metadata
    """
    try:
        quiz_template = {
            "topic": topic,
            "difficulty": difficulty,
            "questions": [],
            "total_questions": 5,
            "time_limit_minutes": 10 if difficulty == "beginner" else 20,
            "passing_score": 70,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "quiz_template": quiz_template,
            "message": f"Quiz template created for '{topic}' at {difficulty} level"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create quiz: {str(e)}"
        }


def track_progress(user_id: str, tool_name: str, milestone: str, completed: bool = True) -> dict:
    """
    Tracks learning progress for a user on a specific tool.
    
    Args:
        user_id: Identifier for the user
        tool_name: Name of the tool being learned
        milestone: Description of the milestone (e.g., "Completed basic tutorial")
        completed: Whether the milestone was completed
        
    Returns:
        Dictionary with updated progress information
    """
    try:
        progress_file = f"progress_{user_id}.json"
        
        # Load existing progress
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
        else:
            progress_data = {"user_id": user_id, "tools": {}}
        
        # Update progress
        if tool_name not in progress_data["tools"]:
            progress_data["tools"][tool_name] = {
                "started": datetime.now().isoformat(),
                "milestones": []
            }
        
        progress_data["tools"][tool_name]["milestones"].append({
            "milestone": milestone,
            "completed": completed,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save progress
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Progress tracked: {milestone}",
            "total_milestones": len(progress_data["tools"][tool_name]["milestones"])
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to track progress: {str(e)}"
        }


def get_progress_summary(user_id: str) -> dict:
    """
    Retrieves a summary of all learning progress for a user.
    
    Args:
        user_id: Identifier for the user
        
    Returns:
        Dictionary with complete progress summary
    """
    try:
        progress_file = f"progress_{user_id}.json"
        
        if not os.path.exists(progress_file):
            return {
                "status": "success",
                "message": "No progress recorded yet",
                "tools_count": 0,
                "tools": {}
            }
        
        with open(progress_file, 'r') as f:
            progress_data = json.load(f)
        
        summary = {
            "status": "success",
            "user_id": user_id,
            "tools_count": len(progress_data["tools"]),
            "tools": progress_data["tools"]
        }
        
        return summary
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve progress: {str(e)}"
        }


def manage_learning_session(user_id: str, tool_name: str, action: str, module_name: str = "") -> dict:
    """
    Manages interactive learning sessions for teaching modules step-by-step.
    
    Args:
        user_id: Identifier for the user
        tool_name: Name of the tool being learned
        action: Action to perform (start, next_module, complete_module, get_current)
        module_name: Name of the module for complete_module action
        
    Returns:
        Dictionary with session status and next steps
    """
    try:
        session_file = f"session_{user_id}_{tool_name.lower().replace(' ', '_')}.json"
        
        if action == "start":
            # Initialize new learning session
            session = {
                "user_id": user_id,
                "tool_name": tool_name,
                "started": datetime.now().isoformat(),
                "current_module": 0,
                "modules_completed": [],
                "status": "in_progress"
            }
            with open(session_file, 'w') as f:
                json.dump(session, f, indent=2)
            
            return {
                "status": "success",
                "message": f"Started learning session for {tool_name}",
                "session": session
            }
        
        elif action == "next_module":
            # Move to next module
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session = json.load(f)
                
                session["current_module"] += 1
                with open(session_file, 'w') as f:
                    json.dump(session, f, indent=2)
                
                return {
                    "status": "success",
                    "message": f"Advanced to module {session['current_module']}",
                    "current_module": session["current_module"]
                }
            else:
                return {
                    "status": "error",
                    "error_message": "No active session found. Start a new session first."
                }
        
        elif action == "complete_module":
            # Mark current module as completed
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session = json.load(f)
                
                session["modules_completed"].append({
                    "module_number": session["current_module"],
                    "module_name": module_name if module_name else f"Module {session['current_module']}",
                    "completed_at": datetime.now().isoformat()
                })
                
                with open(session_file, 'w') as f:
                    json.dump(session, f, indent=2)
                
                return {
                    "status": "success",
                    "message": f"Module {session['current_module']} completed!",
                    "modules_completed": len(session["modules_completed"])
                }
            else:
                return {
                    "status": "error",
                    "error_message": "No active session found"
                }
        
        elif action == "get_current":
            # Get current session status
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session = json.load(f)
                return {
                    "status": "success",
                    "session": session
                }
            else:
                return {
                    "status": "success",
                    "message": "No active session",
                    "session": None
                }
        
        else:
            return {
                "status": "error",
                "error_message": f"Unknown action: {action}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to manage session: {str(e)}"
        }


def create_tool_folder(tool_name: str) -> dict:
    """
    Creates a dedicated folder for a specific tool/technology under lessons/.
    Checks if folder exists first.
    
    Args:
        tool_name: Name of the tool (e.g., "LangChain", "FastAPI")
        
    Returns:
        Dictionary with folder path and status
    """
    try:
        folder_name = tool_name.lower().replace(' ', '_').replace('-', '_')
        # Create under lessons/ directory to keep main folder clean
        lessons_dir = os.path.join(os.getcwd(), "lessons")
        folder_path = os.path.join(lessons_dir, folder_name)
        
        # Ensure lessons directory exists
        if not os.path.exists(lessons_dir):
            os.makedirs(lessons_dir)
        
        if os.path.exists(folder_path):
            # Folder already exists
            files = os.listdir(folder_path)
            return {
                "status": "exists",
                "message": f"Folder 'lessons/{folder_name}' already exists",
                "folder_path": folder_path,
                "existing_files": files
            }
        else:
            # Create new folder
            os.makedirs(folder_path)
            return {
                "status": "created",
                "message": f"Created new folder 'lessons/{folder_name}'",
                "folder_path": folder_path,
                "existing_files": []
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create folder: {str(e)}"
        }


def save_to_tool_folder(tool_name: str, filename: str, content: str) -> dict:
    """
    Saves content to a file within the tool's folder under lessons/.
    
    Args:
        tool_name: Name of the tool
        filename: Name of the file to save
        content: Content to write to the file
        
    Returns:
        Dictionary with save status and file path
    """
    try:
        folder_name = tool_name.lower().replace(' ', '_').replace('-', '_')
        lessons_dir = os.path.join(os.getcwd(), "lessons")
        folder_path = os.path.join(lessons_dir, folder_name)
        
        # Ensure folders exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"Saved '{filename}' to lessons/{folder_name}/",
            "file_path": file_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to save file: {str(e)}"
        }


def read_from_tool_folder(tool_name: str, filename: str) -> dict:
    """
    Reads content from a file in the tool's folder under lessons/.
    
    Args:
        tool_name: Name of the tool
        filename: Name of the file to read
        
    Returns:
        Dictionary with file content or error
    """
    try:
        folder_name = tool_name.lower().replace(' ', '_').replace('-', '_')
        lessons_dir = os.path.join(os.getcwd(), "lessons")
        folder_path = os.path.join(lessons_dir, folder_name)
        file_path = os.path.join(folder_path, filename)
        
        if not os.path.exists(file_path):
            return {
                "status": "not_found",
                "message": f"File '{filename}' not found in lessons/{folder_name}/",
                "content": None
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "message": f"Read '{filename}' from lessons/{folder_name}/",
            "content": content,
            "file_path": file_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to read file: {str(e)}",
            "content": None
        }


def assemble_module_file(tool_name: str, module_number: int, lesson: str, examples: str, quiz: str) -> dict:
    """
    Assembles lesson, examples, and quiz into one module markdown file.
    
    Args:
        tool_name: Name of the tool
        module_number: Module number (1, 2, 3, etc.)
        lesson: Teacher's lesson content
        examples: Example agent's code examples
        quiz: Quiz agent's questions
        
    Returns:
        Dictionary with assembled file path
    """
    try:
        # Build comprehensive module content
        module_content = f"""# Module {module_number}

## 📚 Lesson

{lesson}

---

## 💻 Code Examples

{examples}

---

## 📝 Quiz

{quiz}

---

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        filename = f"module_{module_number}.md"
        result = save_to_tool_folder(tool_name, filename, module_content)
        
        # Add absolute path to result for agent reference
        result["absolute_path"] = os.path.abspath(os.path.join("lessons", tool_name, filename))
        
        return result
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to assemble module: {str(e)}"
        }


# =============================================================================
# SPECIALIST AGENTS DEFINITIONS
# =============================================================================

# 1. Researcher Agent - Finds information about AI tools
researcher_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="researcher_agent",
    description="Research specialist that finds comprehensive information about AI tools and technologies.",
    instruction="""
    You are a Research Specialist Agent.
    
    **Your Mission:**
    Research tools/technologies comprehensively and RETURN the findings.
    
    **Your Tool:**
    - `google_search`: Search for information
    
    **Research Protocol:**
    1. Use google_search to find official documentation, GitHub repos, and trusted articles
    2. Identify key information:
       - What the tool does and its main purpose
       - Key features and capabilities
       - Installation and setup requirements
       - Basic usage examples and code snippets
       - Prerequisites and dependencies
       - Community size and ecosystem
       - Pros and cons
    3. Synthesize findings into a clear, comprehensive summary for the user
    
    **Quality Standards:**
    - Prioritize official sources (docs, GitHub, official blogs)
    - Verify information is current (check dates)
    - Provide context about the tool's ecosystem and alternatives
    - Be honest about limitations or complexity
    - Return complete research in clean Markdown format
    """,
    tools=[google_search]
)

# 2. Planner Agent - Creates structured learning plans
planner_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="planner_agent",
    description="Learning plan architect that creates comprehensive, structured learning roadmaps.",
    instruction="""
    You are a Learning Plan Architect.
    
    **Your Mission:**
    Create structured learning roadmaps based on research data provided to you.
    
    **Planning Framework:**
    
    1. **Create roadmap** with these components:
       
       a. **Overview & Prerequisites**
          - Brief introduction to the technology
          - Required prior knowledge
          - Estimated time commitment
       
       b. **Learning Modules** (Break into 5-7 modules)
          - Module 1: Fundamentals
          - Module 2: Core Concepts
          - Module 3: Practical Application
          - Module 4-6: Advanced Topics
          - Module 7: Real-world Projects
          
          For each module specify:
          - Module name and learning objectives
          - Key concepts covered
          - Estimated time
       
       c. **Hands-On Projects** (3 progressive projects)
          - Project 1 (Beginner): Simple, confidence-building
          - Project 2 (Intermediate): Practical, real-world application
          - Project 3 (Advanced): Complex, portfolio-worthy
       
       d. **Resources & Next Steps**
          - Official documentation links
          - Recommended tutorials/courses
          - Community resources
          - Related technologies to explore
    
    2. **Quality Standards:**
    Format in clear Markdown with headers, lists, and emphasis.
    Make modules granular and teachable - each should be completable in 1-2 hours.
    """,
    tools=[]
)

# 3. Example Agent - Generates code examples
example_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="example_agent",
    description="Code example specialist that creates practical, well-commented code demonstrations.",
    instruction="""
    You are a Code Example Specialist.
    
    **Your Mission:**
    Create practical, executable code examples based on the research data provided to you.
    
    **Example Creation Protocol:**
    
    1. **Analyze Research Data** provided to you
    2. **Create Examples** that demonstrate:
       - Basic setup and imports
       - Simple "Hello World" style usage
       - Practical real-world scenarios
       - Common patterns and best practices
       - Error handling
    
    3. **Format Each Example:**
       ```python
       # Example: [Clear title]
       # Purpose: [What this demonstrates]
       
       [Imports]
       
       [Code with inline comments]
       
       # Expected Output:
       # [Show what user should see]
       ```
    
    4. **Provide 3-5 Progressive Examples:**
       - Example 1: Basic usage (beginner)
       - Example 2: Intermediate pattern
       - Example 3: Advanced/real-world scenario
       - Include common pitfalls and solutions
    
    **Quality Standards:**
    - Code must be executable and tested
    - Clear, descriptive comments
    - Show expected outputs
    - Explain WHY, not just WHAT
    - Link to concepts from research.md
    - Use Python unless research indicates otherwise
    
    **Output Format:**
    Return examples in clean Markdown with proper code blocks.
    DO NOT save files - just return the content.
    """,
    tools=[]
)

# 4. Tracker Agent - Manages learning progress
tracker_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="tracker_agent",
    description="Progress tracking and motivation specialist.",
    instruction="""
    You are a Progress Tracker and Motivational Coach.
    
    **Your Tools:**
    - `track_progress`: Record learning milestones
    - `get_progress_summary`: Retrieve complete progress history
    - `load_memory`: Access conversation history and context
    
    **Tracking Protocol:**
    1. When users complete tasks, use track_progress to record:
       - Tool name they're learning
       - Specific milestone completed
       - Completion status
    
    2. Common milestones to track:
       - "Started learning [tool]"
       - "Completed basic tutorial"
       - "Built first project"
       - "Completed quiz with [score]%"
       - "Finished learning plan"
    
    3. When users ask about progress:
       - Use get_progress_summary to retrieve full history
       - Provide encouraging summary
       - Highlight achievements
       - Suggest next steps
    
    **Motivational Approach:**
    - Celebrate all progress, big and small
    - Be specific about achievements
    - Connect progress to goals
    - Provide encouragement during difficulties
    - Suggest concrete next actions
    - Use positive, energizing language
    
    **Always record milestones automatically when users mention completing something!**
    """,
    tools=[track_progress, get_progress_summary, load_memory]
)

# 5. Notifier Agent - Sends notifications and updates
notifier_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="notifier_agent",
    description="Notification and alert specialist for important updates.",
    instruction="""
    You are a Notification Specialist. You create clear, engaging notifications.
    
    **Notification Types:**
    
    1. **Achievement Notifications** 🎉
       - Format: "🎉 **Congratulations!** You've [achievement]"
       - Include what was accomplished and why it matters
       - Suggest next step
    
    2. **Reminder Notifications** ⏰
       - Format: "⏰ **Reminder:** [what to remember]"
       - Be specific and actionable
       - Include deadlines if relevant
    
    3. **Progress Notifications** 📊
       - Format: "📊 **Progress Update:** [status]"
       - Show what's completed vs what remains
       - Motivate to continue
    
    4. **Tip Notifications** 💡
       - Format: "💡 **Pro Tip:** [helpful advice]"
       - Share relevant best practices
       - Keep it actionable
    
    **Style Guidelines:**
    - Use emojis for visual engagement
    - Bold important information
    - Keep messages concise but complete
    - Always end with encouragement or next action
    - Match tone to notification type (celebratory, helpful, informative)
    """,
    tools=[]
)

# 6. Quiz Agent - Creates comprehensive quizzes with gradual difficulty
quiz_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="quiz_agent",
    description="Comprehensive quiz generator with gradual difficulty progression.",
    instruction="""
    You are a Quiz Specialist.
    
    **Your Mission:**
    Create comprehensive quizzes with gradual difficulty based on research data provided to you.
    
    **Quiz Design Principles:**
    
    1. **Comprehensive Coverage**
       - Cover ALL aspects of the research data
       - Test both theory and practical application
       - Include edge cases and nuances
    
    2. **Gradual Difficulty Progression**
       - Start with basic recall questions (Easy)
       - Move to application questions (Medium)
       - End with analysis/synthesis questions (Hard)
       - Clearly label difficulty for each question
    
    3. **Question Types**
       - Multiple choice (with 4 options)
       - True/False (with explanation)
       - Short answer/fill-in-the-blank
       - Code analysis (what does this code do?)
       - Practical scenarios (how would you solve X?)
    
    4. **Quality Standards**
       - Each question tests a specific concept
       - Distractors (wrong answers) are plausible
       - Questions are unambiguous
       - Answers are clearly correct/incorrect
    
    **Quiz Structure:**
    
    For each module quiz, create:
    - **10-15 questions** total
    - **Easy (40%)**: 4-6 questions - recall and comprehension
    - **Medium (40%)**: 4-6 questions - application and analysis
    - **Hard (20%)**: 2-3 questions - synthesis and evaluation
    
    **Format:**
    ```markdown
    ### Question 1 [Easy]
    What is [concept]?
    
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    
    **Answer**: B
    **Explanation**: [Why B is correct and others are wrong]
    
    ---
    
    ### Question 2 [Medium]
    ...
    ```
    
    **Important:**
    - ALWAYS read research.md from the tool folder first using `read_from_tool_folder`
    - Base ALL questions on the actual research data
    - Don't make up facts - stick to the research
    - Provide detailed explanations for each answer
    - Include a summary at the end: "Score X/Y to pass"
    - DO NOT save files - just return the quiz content
    """,
    tools=[]
)

# 7. Teacher Agent - Creates comprehensive lessons for modules
teacher_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="teacher_agent",
    description="Expert educator that creates comprehensive, engaging lessons for each module.",
    instruction="""
    You are an Expert Teacher and Curriculum Designer.
    
    **Your Mission:**
    Create comprehensive, engaging lessons that teach concepts clearly and thoroughly.
    
    **Your Mission:**
    Create comprehensive lessons based on research and roadmap data provided to you.
    
    **Lesson Creation Protocol:**
    
    1. **Analyze Provided Data:**
       - Review research data
       - Review roadmap structure
    
    2. **For Each Module**, create a comprehensive lesson with:
       
       **a. Module Introduction (Why it matters)**
       - Hook: Why this module is important
       - Learning objectives (what they'll be able to do)
       - Prerequisites (what they should know)
       - Estimated time
       
       **b. Core Concepts (What to learn)**
       - Break complex ideas into simple explanations
       - Use analogies and real-world comparisons
       - Define technical terms clearly
       - Build from basics to advanced
       - Include diagrams/visual descriptions when helpful
       
       **c. Key Takeaways**
       - Bullet points of must-remember concepts
       - Common pitfalls and how to avoid them
       - Best practices
       
       **d. Practice Guidance**
       - Suggest what to try next
       - Link to examples (note: examples provided separately)
       - Preview next module connection
    
    **Teaching Style:**
    - Clear, conversational language
    - Patient and encouraging tone
    - Use stories and analogies
    - Anticipate confusion points
    - Progressive complexity
    
    **Output Format:**
    Return lesson content in clean Markdown format.
    Use headers, lists, emphasis, and code snippets where appropriate.
    DO NOT save files - just return the content.
    
    **Remember:**
    - Base EVERYTHING on provided research data
    - Reference provided roadmap for module scope
    - Focus on TEACHING, not just information dump
    - Make it engaging and accessible
    """,
    tools=[]
)

# =============================================================================
# MAIN ORCHESTRATOR AGENT
# =============================================================================

# Main Agent - Orchestrates specialist agents (ADK recommended pattern)
main_agent = LlmAgent(
    model=Gemini(model=MODEL_NAME, retry_options=retry_config),
    name="main_agent",
    description="Master orchestrator for the newToolNoProblem AI Learning Assistant.",
    instruction="""
    You are the Master Orchestrator for newToolNoProblem - an intelligent learning assistant.
    
    **Your Role:**
    You are the central hub. You manage all files and coordinate your team of specialists.
    Your specialists DO NOT touch files. You must read/write files for them.
    
    **Your Specialist Team:**
    - `researcher_agent`: Researches tools (Returns content only)
    - `planner_agent`: Creates roadmaps (Returns content only)
    - `teacher_agent`: Creates lessons (Returns content only)
    - `example_agent`: Generates examples (Returns content only)
    - `quiz_agent`: Creates quizzes (Returns content only)
    - `tracker_agent`: Tracks progress
    - `notifier_agent`: Sends messages
    
    **Complete Workflow:**
    
    **Phase 1: Research & Planning**
    User: "I want to learn [tool]"
    
    1. **Setup:**
       - Call `create_tool_folder(tool_name)`
    
    2. **Research:**
       - Check if `research.md` exists using `read_from_tool_folder`
       - If NOT found:
         - Ask `researcher_agent` to research the tool
         - Save their response to `research.md` using `save_to_tool_folder`
       - If found: Read it to use for next steps
    
    3. **Planning:**
       - Check if `roadmap.md` exists
       - If NOT found:
         - Read `research.md` content
         - Ask `planner_agent`: "Create a learning roadmap based on this research: [insert research content]"
         - Save their response to `roadmap.md`
       - Present roadmap to user
    
    **Phase 2: Module Generation**
    User: "Start module 1"
    
    1. **Prepare Context:**
       - Read `research.md` content
       - Read `roadmap.md` content
    
    2. **Generate Content (Parallel-ish):**
       - Ask `teacher_agent`: "Create a lesson for Module 1 based on this research: [content] and roadmap: [content]"
       - Ask `example_agent`: "Create code examples for Module 1 based on this research: [content]"
       - Ask `quiz_agent`: "Create a quiz for Module 1 based on this research: [content]"
    
    3. **Assemble & Save:**
       - Call `assemble_module_file` with the outputs from the 3 agents
       - This will save `module_1.md` automatically
    
    4. **Present & Track:**
       - Read the saved `module_1.md` and show it to the user
       - **CRITICAL:** Tell the user: "I've saved the complete module to: [absolute_path]"
       - Suggest: "You can open this file in your favorite Markdown viewer (like VS Code or Obsidian) for the best experience."
       - Call `tracker_agent` to record progress
       - Call `notifier_agent` to celebrate
    
    **Key Rules:**
    - **YOU manage the files.** Agents just generate text.
    - **ALWAYS pass context.** Agents don't know what "research.md" is unless you read it and paste the content in your prompt to them.
    - **Save everything.** Don't lose the agents' hard work.
    """,
    tools=[
        AgentTool(agent=researcher_agent),
        AgentTool(agent=planner_agent),
        AgentTool(agent=teacher_agent),
        AgentTool(agent=example_agent),
        AgentTool(agent=quiz_agent),
        AgentTool(agent=tracker_agent),
        AgentTool(agent=notifier_agent),
        FunctionTool(func=create_tool_folder),
        FunctionTool(func=save_to_tool_folder),
        FunctionTool(func=read_from_tool_folder),
        FunctionTool(func=assemble_module_file)
    ]
)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    # Initialize Rich console for beautiful markdown rendering
    console = Console()
    
    print("=" * 70)
    print("        🎓 newToolNoProblem - AI Learning Assistant 🚀")
    print("=" * 70)
    print("\n📌 Mission: Help developers master emerging AI tools quickly!")
    print("\n💡 Features:")
    print("  • Comprehensive research & learning roadmaps")
    print("  • Module-by-module structured lessons")
    print("  • Practical code examples (3-5 per module)")
    print("  • Comprehensive quizzes with gradual difficulty")
    print("  • Progress tracking & motivation")
    print("\n💾 Organization: All lessons saved to lessons/[tool_name]/ folder")
    print("\n" + "=" * 70)
    
    # Initialize Session Service
    session_service = InMemorySessionService()
    session_id = "user_session"
    user_id = "learner_001"
    
    await session_service.create_session(
        app_name="newToolNoProblem",
        user_id=user_id,
        session_id=session_id
    )
    
    # Initialize Memory Service for long-term context
    memory_service = InMemoryMemoryService()
    
    # Initialize Runner with Logging Plugin
    runner = Runner(
        agent=main_agent,
        app_name="newToolNoProblem",
        session_service=session_service,
        memory_service=memory_service,
        plugins=[LoggingPlugin()]
    )
    
    print("\n✅ System ready! Type 'help' for commands or 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("\n👋 Goodbye! Keep learning, keep growing! 🚀")
            break
        
        if user_input.lower() == "help":
            print("\n📖 Available Commands:")
            print("  • 'learn [tool name]' - Research & create learning roadmap")
            print("  • 'start module 1' - Generate complete module (lesson+examples+quiz)")
            print("  • 'progress' - Check your learning progress")
            print("  • 'help' - Show this help message")
            print("  • 'exit' - Quit the assistant")
            print("\n💡 Tip: All lessons saved to lessons/[tool_name]/ folder\n")
            continue
            
        if not user_input.strip():
            continue
        
        print("\n🤖 Assistant:")
        print("-" * 70)
        
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=types.Content(parts=[types.Part(text=user_input)])
            ):
                if event.is_final_response() and event.content:
                    response_text = event.content.parts[0].text
                    # Render markdown beautifully using Rich
                    md = Markdown(response_text)
                    console.print(md)
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'help' for assistance.")
        
        print("-" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
