import os
from typing import Callable, List, Any, AsyncGenerator

from llama_index.core.base.llms.types import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.llms.openai.utils import is_function_calling_model
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import ReActAgent, FunctionAgent
from workflows.events import Event
from workflows.handler import WorkflowHandler

from remail.interfaces.llm.enums.llm_model import LLMModel


class StatefulLlmController:
    """
    Stateful LLM Controller using OpenAI-like model with agent tools.
    """

    def __init__(
        self,
        model: LLMModel,
        temperature: float = 0.28,
        max_tokens: int = 512,
    ):
        self.model_name = model.value
        self.api_key = os.getenv("LLM_API_KEY")
        self.api_base = os.getenv("LLM_BASE_URL")
        self.temperature = temperature
        self.max_tokens = max_tokens

        # OpenAI-like LLM für LlamaIndex
        self.llm = OpenAI(
            model=self.model_name, #self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            is_function_calling_model=True
        )

        # Liste der Agent-Tools
        self.tools: List[FunctionTool] = []
        self.agent: FunctionAgent | None = None

    def add_tool(
        self, name: str, description: str, fn: Callable[..., Any]
    ):
        """
        Add a function as a tool to the agent.
        """
        tool = FunctionTool.from_defaults(fn=fn, name=name, description=description)
        self.tools.append(tool)

    def build_agent(self, system_prompt: str):
        """
        Initialize the agent with all added tools.
        """
        if not self.tools:
            raise ValueError("No tools added. Add at least one tool before building agent.")

        self.agent = FunctionAgent(
            tools=self.tools,
            llm=self.llm,
            system_prompt=system_prompt,
        )

    def query(self, user_prompt: str) -> WorkflowHandler:
        """
        Execute a user prompt through the agent, handling tools and sequential calls.
        """
        if self.agent is None:
            raise RuntimeError("Agent not built. Call build_agent() first.")

        response = self.agent.run(user_msg=user_prompt, )#max_iterations=5)
        return response

    #todo: add support for database connection (nlsql)
