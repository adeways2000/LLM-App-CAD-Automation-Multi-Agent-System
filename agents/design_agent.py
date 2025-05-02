"""
Design Agent for Company CAD Automation Multi-Agent System

This module implements the Design Agent that focuses on design intent, requirements,
and constraints, helping to interpret design requirements and validate designs.
"""
import os
import streamlit as st
from typing import Dict, List, Any, TypedDict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json
from langchain.globals import get_verbose

class DesignAgent:
    """
    Design Agent that focuses on design intent, requirements, and constraints.
    """
    
    def __init__(self, llm: ChatOpenAI = None):
        """
        Initialize the Design Agent.
        
        Args:
            model_name: The name of the LLM model to use
        """
        if llm is None:
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.5,
                openai_api_key=os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
            )
        else:
            self.llm = llm
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the prompt template for the Design Agent.
        
        Returns:
            ChatPromptTemplate: The prompt template
        """
        return ChatPromptTemplate.from_template("""
        You are the Design Agent in a CAD automation system for Company GmbH.
        Your role is to interpret design requirements, suggest design alternatives,
        validate designs against requirements, and document design decisions.

        Task: {task}
        Current Design State: {design_state}
        CAD Model State: {cad_model_state}
        User Requirements: {user_input}

        Based on the task and current states, you need to:
        1. Interpret design requirements and specifications
        2. Identify design constraints and parameters
        3. Suggest design approaches or alternatives
        4. Validate designs against requirements
        5. Document design decisions and rationales

        Provide your analysis and recommendations in the following JSON format:
        ```json
        {
            "interpretation": "Your interpretation of the design requirements",
            "constraints": {
                "constraint1": "value1",
                "constraint2": "value2"
            },
            "parameters": {
                "parameter1": "value1",
                "parameter2": "value2"
            },
            "design_alternatives": [
                {
                    "approach": "Description of design approach 1",
                    "pros": ["pro1", "pro2"],
                    "cons": ["con1", "con2"]
                }
            ],
            "validation": "Assessment of how well the current design meets requirements",
            "recommendations": "Specific recommendations for the design",
            "documentation": "Documentation of design decisions and rationales"
        }
        ```
        """)
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current state and perform design analysis.
        
        Args:
            state: The current workflow state
            
        Returns:
            Updated workflow state
        """
        # Extract the design task from the state
        design_tasks = state["design_state"].get("tasks", [])
        if not design_tasks:
            state["errors"].append("No design tasks found for Design Agent")
            return state
        
        # Process the most recent task
        current_task = design_tasks[-1]
        
        # Process with the LLM
        response = self.chain.invoke({
            "task": current_task,
            "design_state": json.dumps(state["design_state"]),
            "cad_model_state": json.dumps(state["cad_model_state"]),
            "user_input": state["user_input"]
        })
        
        # Extract the JSON response
        response_content = response.content
        json_start = response_content.find('```json') + 7
        json_end = response_content.find('```', json_start)
        json_str = response_content[json_start:json_end].strip()
        
        try:
            design_response = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            design_response = {
                "interpretation": "Failed to parse JSON response",
                "constraints": {},
                "parameters": {},
                "design_alternatives": [],
                "validation": "Error in Design agent response",
                "recommendations": "Error in Design agent response",
                "documentation": "Error in Design agent response"
            }
            state["errors"].append("Design agent produced invalid JSON response")
        
        # Update the state with the results
        updated_state = state.copy()
        
        # Update design state with new information
        updated_state["design_state"] = {
            **updated_state["design_state"],
            "constraints": design_response["constraints"],
            "parameters": design_response["parameters"],
            "design_alternatives": design_response["design_alternatives"],
            "validation": design_response["validation"],
            "recommendations": design_response["recommendations"],
            "documentation": design_response["documentation"]
        }
        
        # Remove the processed task
        updated_state["design_state"]["tasks"] = design_tasks[:-1]
        
        # Add message to the state
        updated_state["messages"].append({
            "role": "design_agent",
            "content": f"Design Analysis:\n\nInterpretation: {design_response['interpretation']}\n\nConstraints: {json.dumps(design_response['constraints'], indent=2)}\n\nRecommendations: {design_response['recommendations']}"
        })
        
        # Set next agent back to coordinator
        updated_state["next_agent"] = "coordinator_agent"
        
        return updated_state
