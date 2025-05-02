"""
CAD Agent for Company CAD Automation Multi-Agent System

This module implements the CAD Agent that handles direct interactions with CAD systems
through Company's CAD connectors, including visualization capabilities.
"""
import os
import json
from typing import Dict, List, Any, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import streamlit as st

class CADOperation(TypedDict):
    operation_type: str  # create, modify, delete
    element_type: str  # point, line, curve, surface, solid, etc.
    parameters: Dict[str, Any]
    expected_outcome: str

class CADAgent:
    """
    CAD Agent handling CAD operations and visualization.
    """
    
    def __init__(self, llm: ChatOpenAI = None):
        self.llm = llm or self._default_llm()
        self.connector = self._init_connector()
        self.visualizer = self._init_visualizer()
        self.chain = self._create_prompt() | self.llm

    def _default_llm(self):
        return ChatOpenAI(
            model="gpt-4",
            temperature=0.5,
            openai_api_key=os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        )

    def _init_connector(self):
        """Initialize CAD system connector with UI-friendly formatting"""
        class MockCADConnector:
            def execute(self, operation: CADOperation):
                # Format operation for UI compatibility
                formatted_op = {
                    "type": operation["operation_type"],
                    "element": operation["element_type"],
                    "parameters": operation["parameters"]
                }
                return {
                    "status": "success",
                    "operation": formatted_op,
                    "visualization": self._generate_visualization(operation),
                    "metadata": {"execution_time": 0.5}
                }
            
            def _generate_visualization(self, operation: CADOperation):
                op_type = operation["operation_type"]
                element = operation["element_type"]
                return (
                    f"https://cad-visualization.example.com/"
                    f"{op_type}-{element}-{hash(json.dumps(operation))}.png"
                )
        
        return MockCADConnector()

    def _init_visualizer(self):
        """Initialize visualization engine with view persistence"""
        class VisualizationEngine:
            views = ["2d", "3d", "section"]
            
            def __init__(self):
                self.view_cache = {}
            
            def get_view(self, view_type: str, elements: List[str]):
                cache_key = f"{view_type}-{'-'.join(elements)}"
                if cache_key not in self.view_cache:
                    self.view_cache[cache_key] = (
                        f"https://cad-visualization.example.com/"
                        f"{view_type}?elements={','.join(elements)}"
                    )
                return self.view_cache[cache_key]
        
        return VisualizationEngine()

    def _create_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template("""
        As CAD Agent for Company GmbH, translate design instructions into CAD operations.
        
        Task: {task}
        Current Model: {current_state}
        Constraints: {constraints}
        
        Generate JSON with:
        - operations: List of CAD operations
        - visualization_needs: Required views
        - parameters: Technical specs
        
        Format:
        ```json
        {{
            "reasoning": "...",
            "operations": [
                {{
                    "type": "create|modify|delete",
                    "element": "element_type",
                    "params": {{...}},
                    "expected": "..."
                }}
            ],
            "visualization": {{
                "views": ["2d", "3d", "section"],
                "focus_elements": ["element_id"]
            }},
            "status": "complete|partial"
        }}
        ```
        """)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process CAD tasks and generate visualizations"""
        state = state.copy()
        cad_state = state.setdefault("cad_model_state", {})
        tasks = cad_state.get("tasks", [])
        
        # Initialize visualization structure if missing
        cad_state.setdefault("visualization", {
            "views": {},
            "operations": [],
            "latest_view": None
        })
        
        if not tasks:
            state["errors"].append("No CAD tasks provided")
            return state

        try:
            # Process latest task
            task = tasks.pop()
            response = self.chain.invoke({
                "task": task,
                "current_state": json.dumps(cad_state),
                "constraints": json.dumps(state["design_state"].get("constraints", {}))
            })
            
            # Parse response
            operations = self._parse_response(response.content)
            
            # Execute operations
            results = []
            visualization_data = cad_state["visualization"]
            
            for op in operations["operations"]:
                result = self.connector.execute(op)
                results.append(result)
                
                # Store visualization
                view_url = result["visualization"]
                visualization_data["views"][op["type"]] = view_url
                visualization_data["latest_view"] = view_url
                visualization_data["operations"].append(result["operation"])

            # Generate requested views
            for view_type in operations.get("visualization", {}).get("views", []):
                visualization_data["views"][view_type] = self.visualizer.get_view(
                    view_type, 
                    operations["visualization"]["focus_elements"]
                )

            # Update status
            cad_state["status"] = operations["status"]
            cad_state["tasks"] = tasks

            # Add visualization message
            state["messages"].append({
                "role": "cad_agent",
                "content": {
                    "text": operations["reasoning"],
                    "visualizations": [
                        {"type": t, "url": u} 
                        for t, u in visualization_data["views"].items()
                    ],
                    "primary_view": visualization_data["latest_view"]
                }
            })

        except Exception as e:
            state["errors"].append(f"CAD Error: {str(e)}")
            cad_state["status"] = "error"

        state["next_agent"] = "coordinator"
        return state

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Robust JSON parsing with validation"""
        try:
            # Extract JSON block
            json_str = response.split("```json")[1].split("```")[0].strip()
            data = json.loads(json_str)
            
            # Validate required fields
            if not all(key in data for key in ["operations", "status"]):
                raise ValueError("Missing required fields in CAD response")
                
            return data
            
        except (IndexError, json.JSONDecodeError, ValueError) as e:
            error_msg = f"Invalid CAD response format: {str(e)}"
            raise ValueError(error_msg) from e

# Example usage
if __name__ == "__main__":
    agent = CADAgent()
    sample_state = {
        "cad_model_state": {
            "tasks": ["Create a gear with 24 teeth"],
            "elements": {"gears": []},
            "visualization": {
                "views": {},
                "operations": [],
                "latest_view": None
            }
        },
        "design_state": {
            "constraints": {"material": "steel"}
        }
    }
    
    result = agent.process(sample_state)
    print("Generated Visualization Data:")
    print(json.dumps(result["cad_model_state"]["visualization"], indent=2))