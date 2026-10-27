from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from openai import OpenAI
from pydantic import BaseModel

MAX_ITERATIONS = 10

REACT_PROMPT = (
    "You are an autonomous coding assistant. Follow this execution loop strictly:\n"
    "1. EXPLORE FIRST: Always list the directory or search the codebase to identify existing files before taking action.\n"
    "2. PREFER EDITING: Never create a new file if an existing file can be modified or extended. Only create a file if no relevant file exists after inspecting the codebase.\n"
    "3. INSPECT BEFORE EDITING: Always read existing files before editing or importing from them. Never invent or assume file contents; rely solely on actual tool outputs.\n"
    "4. TOOL CALLS: Issue exactly ONE tool call per turn. Parallel calls are forbidden.\n"
    "5. PERSISTENCE: Save all code changes via file-writing/editing tools, never as markdown code blocks in the chat response.\n"
    "6. TESTING: Always run tests for modified code. If project tests exist, run them; only create a temporary test file if no test framework or test file is present.\n"
    "7. COMPLETION: Stop calling tools and reply in plain text only when the task is fully completed."
)

PLANNER_PROMPT = """
You are an expert software execution planner.

Your goal is to synthesize the task objective, repository structure, and the Explorer's diagnostic analysis into a structured, executable coding plan.

### Instructions:
- **summary**: Provide a concise summary (1-3 sentences) explaining the root cause and the overall strategy for the fix.
- **target_files**: List only the specific, relevant file paths that must be modified or created. Keep the blast radius minimal based on the Explorer's findings.
- **steps**: Provide an ordered sequence of clear, actionable instructions. Focus on intent, logic changes, and acceptance criteria rather than low-level tool calls or exact diffs. The executor should know exactly what behavior to implement in each step.
- **verification_command**: Provide a single, deterministic command (e.g., a specific `pytest` command, test runner script, or reproduction command) that the executor will run to confirm the issue is completely resolved.
/no_think
"""

EXPLORER_PROMPT = """
You are an expert diagnostic agent specialized in root-cause analysis for software bugs.

Your goal is to inspect the codebase, reproduce the reported issue, and identify the exact lines and files responsible.
### Protocol:
1. **Reconnaissance**: Inspect directory structures and locate configuration/dependency files (e.g., package.json, pyproject.toml).
2. **Reproduction**: Run relevant test suites (e.g., `pytest`, `npm test`) or inspect log outputs to confirm failing conditions.
3. **Trace & Isolate**: Read relevant source files and track data flow leading to the failure. Minimize tool calls by inspecting only suspected code paths.
4. **Handoff Generation**: Once identified, synthesize findings. Do NOT attempt to fix the bug yourself.

IMPORTANT: When you are finished with the inspection do not call any tools and just respond in text. /no_think
"""

class Plan(BaseModel):
    summary:str
    target_files:list[str]
    steps:list[str]
    verify_command:str

class StopReason(Enum):
    TaskFinished = 1
    NeedApproval = 2
    MaxIterations = 3

@dataclass
class ExecutionResult:
    stop_reason:StopReason
    info:str


class AgentSettings:
    def __init__(self,url:str,api_key:str,model:str,cwd:str,task:str):
        self.client = OpenAI(base_url=url,api_key=api_key)
        self.model = model
        self.cwd = cwd
        self.task = task
        
class AgentState(Enum):
    Executing = 1
    WaitingForApproval = 2
    Exploring = 3
    Planning = 4
    Verifying = 5

class AgentStrategyType(Enum):
    ReAct = 1
    PlanAndSolve = 2
    
class AgentStrategy(ABC):
    @abstractmethod
    def run(self,approved:bool) -> ExecutionResult:
        pass
    