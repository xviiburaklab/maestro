import uuid
import os
from typing import Dict, Any, List
from common.schemas import ExecutionStep
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class DAGPlan(BaseModel):
    steps: List[ExecutionStep] = Field(description="List of execution steps representing the DAG plan for the user request.")

class LocalHeuristicPlanner:
    async def plan(self, user_input: str, context: dict) -> List[ExecutionStep]:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "sk-your-openai-api-key-here":
            # Fallback to heuristic if key is missing
            trigger_username = user_input.split(" ")[-1].strip() if " " in user_input else "agent_user"
            return [
                ExecutionStep(
                    step_id="step_1", service="user-service", action="create_user",
                    params={"username": trigger_username, "email": f"{trigger_username}@example.com"},
                    undo_action="delete_user", undo_params={"username": trigger_username}
                )
            ]

        llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)
        structured_llm = llm.with_structured_output(DAGPlan)
        
        system_prompt = (
            "You are an AI orchestrator for a microservices platform. "
            "You MUST break down the user reqest into a sequence of ExecutionStep tasks. "
            "Available services: user-service, auth-service, notification-service. "
            "Actions: create_user, delete_user, assign_role, remove_role, send_welcome, etc. "
            "Return the logical execution plan."
        )
        
        response = structured_llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ])
        
        return response.steps
