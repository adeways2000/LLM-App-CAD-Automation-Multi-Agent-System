"""
Coordinator Agent for CAD Automation Multi-Agent System

This module implements the Coordinator Agent that orchestrates the overall workflow,
delegates tasks to specialized agents, and maintains the global state of the system.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from typing import Dict, List, Any, TypedDict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.globals import set_verbose, get_verbose
import json

# Define the state structure
class CADWorkflowState(TypedDict):
    user_input: str
    current_stage: str
    cad_model_state: Dict[str, Any]
    design_state: Dict[str, Any]
    analysis_state: Dict[str, Any]
    knowledge_context: Dict[str, Any]
    messages: List[Dict[str, Any]]
    errors: List[str]
    next_agent: Optional[str]

class CoordinatorAgent:
    """
    Coordinator Agent that orchestrates the overall workflow and delegates tasks
    to specialized agents.
    """
    
    def __init__(self, llm: ChatOpenAI = None, model_name: str = "gpt-4"):
        """
        Initialize with either an existing LLM or model name
        
        Args:
            model_name: The name of the LLM model to use
        """

        if llm is None:
           self.llm = ChatOpenAI(
               model="gpt-4",
               temperature=0.7,
               openai_api_key=os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
            )
        else:
            # Use provided LLM instance
            self.llm = llm

        self.prompt = self._create_prompt()
        self.chain = self.prompt | self.llm
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the prompt template for the Coordinator Agent.
        
        Returns:
            ChatPromptTemplate: The prompt template
        """
        return ChatPromptTemplate.from_template("""
        You are the Coordinator Agent in a CAD automation system for Company.
        Your role is to understand user requests, break them down into subtasks,
        and coordinate other specialized agents to complete the CAD workflow.

        Available specialized agents:
        1. CAD Agent: Handles direct interactions with CAD systems through Company's CAD connectors
        2. Design Agent: Focuses on design intent, requirements, and constraints
        3. Analysis Agent: Performs engineering analysis, optimization, and validation
        4. Knowledge Agent: Provides domain knowledge, standards, and best practices

        Current workflow state:
        User Input: {user_input}
        Current Stage: {current_stage}
        CAD Model Status: {cad_model_state}
        Design Status: {design_state}
        Analysis Status: {analysis_state}

        Based on the current state, determine the next action:
        1. Delegate to CAD Agent for direct CAD operations
        2. Delegate to Design Agent for design considerations
        3. Delegate to Analysis Agent for engineering analysis
        4. Delegate to Knowledge Agent for information retrieval
        5. Complete the workflow if all tasks are done

        Provide your reasoning and the next action to take in the following JSON format:
        ```json
        {
            "reasoning": "Your detailed reasoning here",
            "next_agent": "cad_agent|design_agent|analysis_agent|knowledge_agent|complete",
            "task_description": "Detailed description of the task for the next agent"
        }
        ```
        """)
    
    def process(self, state: CADWorkflowState) -> CADWorkflowState:
        """
        Process the current state and determine the next action.
        
        Args:
            state: The current workflow state
            
        Returns:
            Updated workflow state
        """
        # Process the current state
        response = self.chain.invoke({
            "user_input": state["user_input"],
            "current_stage": state["current_stage"],
            "cad_model_state": json.dumps(state["cad_model_state"]),
            "design_state": json.dumps(state["design_state"]),
            "analysis_state": json.dumps(state["analysis_state"])
        })
        
        # Extract the JSON response
        response_content = response.content
        json_start = response_content.find('```json') + 7
        json_end = response_content.find('```', json_start)
        json_str = response_content[json_start:json_end].strip()
        
        try:
            decision = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            decision = {
                "reasoning": "Failed to parse JSON response",
                "next_agent": "error",
                "task_description": "Error in coordinator agent response"
            }
            state["errors"].append("Coordinator agent produced invalid JSON response")
        
        # Update the state based on the response
        updated_state = state.copy()
        updated_state["next_agent"] = decision["cad_agent"]
        updated_state["messages"].append({
            "role": "coordinator_agent",
            "content": decision["reasoning"]
        })
        
        # Update the current stage
        if decision["next_agent"] == "complete":
            updated_state["current_stage"] = "completed"
        else:
            updated_state["current_stage"] = f"delegated_to_{decision['next_agent']}"
        
        # Add the task description to the appropriate agent's state
        if decision["next_agent"] == "cad_agent":
            if "tasks" not in updated_state["cad_model_state"]:
                updated_state["cad_model_state"]["tasks"] = []
            updated_state["cad_model_state"]["tasks"].append(decision["task_description"])
        elif decision["next_agent"] == "design_agent":
            if "tasks" not in updated_state["design_state"]:
                updated_state["design_state"]["tasks"] = []
            updated_state["design_state"]["tasks"].append(decision["task_description"])
        elif decision["next_agent"] == "analysis_agent":
            if "tasks" not in updated_state["analysis_state"]:
                updated_state["analysis_state"]["tasks"] = []
            updated_state["analysis_state"]["tasks"].append(decision["task_description"])
        elif decision["next_agent"] == "knowledge_agent":
            if "tasks" not in updated_state["knowledge_context"]:
                updated_state["knowledge_context"]["tasks"] = []
            updated_state["knowledge_context"]["tasks"].append(decision["task_description"])
        
        return updated_state
    
    def route(self, state: CADWorkflowState) -> str:
        """
        Determine which agent should handle the current state.
        
        Args:
            state: The current workflow state
            
        Returns:
            The name of the next agent to call
        """
        return state.get("next_agent", "coordinator_agent")
