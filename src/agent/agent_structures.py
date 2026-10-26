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

PLANNER_PROMPT = (
    "You are an expert planner for coding tasks"
    "Given a directory structure and a given objective issue a step by step to be followed by a LLM with precise instructions and function calls"
    "Supply the function calls arguments in json form"
)

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
    Idle = 1
    WaitingForApproval = 2
    Executing = 3
    Exploring = 4
    Planning = 5
    Verifying = 6

class AgentStrategyType(Enum):
    ReAct = 1
    PlanAndSolve = 2
    
class AgentStrategy(ABC):
    @abstractmethod
    def run(self,approved:bool) -> ExecutionResult:
        pass
    