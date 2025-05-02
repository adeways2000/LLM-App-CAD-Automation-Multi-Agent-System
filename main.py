"""
Main Application for Company CAD Automation Multi-Agent System

This module implements the main application that integrates all agents using LangGraph
and provides the workflow for the CAD automation system.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import TypedDict, Dict, List, Any, Literal, Optional, Union
from langgraph.graph import StateGraph, END
import operator
import streamlit as st

# Import the agents
from agents.coordinator_agent import CoordinatorAgent, CADWorkflowState
from agents.cad_agent import CADAgent
from agents.design_agent import DesignAgent
from agents.analysis_agent import AnalysisAgent
from agents.knowledge_agent import KnowledgeAgent

# Load environment variables first
load_dotenv()


def get_openai_key() -> str:
    """Get OpenAI API key from environment or Streamlit secrets"""
    key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "OpenAI API key not found. Please set it in either:\n"
            "1. .env file: OPENAI_API_KEY=your-key-here\n"
            "2. Streamlit secrets: st.secrets['OPENAI_API_KEY'] = your-key-here"
        )
    return key

class CADAutomationApp:
    """
    Main application class that integrates all agents using LangGraph.
    """
    
    def __init__(self):
        """Initialize the CAD Automation Application."""
        try:
            # Initialize shared LLM first
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                openai_api_key=get_openai_key()
            )
            
            # Initialize agents with shared LLM
            self.coordinator_agent = CoordinatorAgent(llm=self.llm)
            self.cad_agent = CADAgent(llm=self.llm)
            self.design_agent = DesignAgent(llm=self.llm)
            self.analysis_agent = AnalysisAgent(llm=self.llm)
            self.knowledge_agent = KnowledgeAgent(llm=self.llm)
            
            # Create and compile the graph
            self.graph = self._create_graph()
            self.app = self.graph.compile()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize application: {str(e)}") from e

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state graph for the application."""
        workflow = StateGraph(CADWorkflowState)
        
        # Add nodes
        workflow.add_node("coordinator", self.coordinator_agent.process)
        workflow.add_node("cad_agent", self.cad_agent.process)
        workflow.add_node("design_agent", self.design_agent.process)
        workflow.add_node("analysis_agent", self.analysis_agent.process)
        workflow.add_node("knowledge_agent", self.knowledge_agent.process)

        # Define routing logic
        def route_to_agent(state: CADWorkflowState) -> str:
            next_agent = state.get("next_agent", "coordinator")
            if next_agent == "complete":
                return END
            return next_agent  # Returns one of the agent node names

        # Configure edges
        workflow.add_conditional_edges(
            source="coordinator",
            path=route_to_agent,
            path_map={
                "cad_agent": "cad_agent",
                "design_agent": "design_agent",
                "analysis_agent": "analysis_agent",
                "knowledge_agent": "knowledge_agent",
                END: END
            }
        )

        # Connect all agents back to coordinator
        for agent in ["cad_agent", "design_agent", 
                    "analysis_agent", "knowledge_agent"]:
            workflow.add_edge(agent, "coordinator")

        # Set the initial entry point
        workflow.set_entry_point("coordinator")
        
        return workflow

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request through the multi-agent system."""
        initial_state: CADWorkflowState = {
            "user_input": user_input,
            "current_stage": "initial",
            "cad_model_state": {
                "elements": {},
                "parameters": {},
                "visualization_url": None
            },
            "design_state": {
                "requirements": {},
                "constraints": {}
            },
            "analysis_state": {
                "last_analysis": {},
                "results": {}
            },
            "knowledge_context": {
                "standards": [],
                "best_practices": []
            },
            "messages": [{"role": "user", "content": user_input}],
            "errors": [],
            "next_agent": "coordinator"
        }
        
        try:
            return self.app.invoke(initial_state)
        except Exception as e:
            return {
                **initial_state,
                "errors": [str(e)],
                "current_stage": "error"
            }

if __name__ == "__main__":
    try:
        app = CADAutomationApp()
        result = app.process_request(
            "Design a gear assembly with 5 gears. Main gear: 100mm diameter, 24 teeth, 50Nm torque, 1000 RPM."
        )
        
        print("Final Messages:")
        for message in result["messages"]:
            print(f"\n[{message['role']}]: {message['content']}")
            
        if result["errors"]:
            print("\nErrors:")
            for error in result["errors"]:
                print(f"- {error}")
                
    except Exception as e:
        print(f"Critical error: {str(e)}")