"""
Knowledge Agent for Company CAD Automation Multi-Agent System

This module implements the Knowledge Agent that provides domain knowledge,
standards, and best practices for engineering and CAD operations.
"""

from typing import Dict, List, Any, TypedDict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json

class KnowledgeAgent:
    """
    Knowledge Agent that provides domain knowledge, standards, and best practices.
    """
    
    def __init__(self, llm: ChatOpenAI = None):
        """
        Initialize the Knowledge Agent.
        
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
        # In a real implementation, this would connect to a knowledge base
        self.knowledge_base = self._mock_knowledge_base()
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the prompt template for the Knowledge Agent.
        
        Returns:
            ChatPromptTemplate: The prompt template
        """
        return ChatPromptTemplate.from_template("""
        You are the Knowledge Agent in a CAD automation system for Company GmbH.
        Your role is to provide domain knowledge, engineering standards, and best practices
        to support the CAD workflow.

        Task: {task}
        Current Knowledge Context: {knowledge_context}
        Related Domain: {domain}
        Query: {query}

        Knowledge Domains:
        1. Mechanical Engineering: Materials, mechanics, manufacturing processes
        2. Electrical Engineering: Circuits, components, power systems
        3. Civil Engineering: Structures, materials, building codes
        4. Aerospace Engineering: Aerodynamics, materials, safety standards
        5. CAD Best Practices: Modeling techniques, file organization, version control

        Based on the query and domain, provide relevant knowledge, standards, and best practices.
        Include references to specific standards or sources when applicable.

        Provide your response in the following JSON format:
        ```json
        {
            "domain_knowledge": "Comprehensive domain knowledge related to the query",
            "standards": [
                {
                    "standard_name": "Name of the standard",
                    "description": "Brief description",
                    "relevance": "Why this standard is relevant"
                }
            ],
            "best_practices": [
                "Best practice 1",
                "Best practice 2"
            ],
            "references": [
                "Reference 1",
                "Reference 2"
            ],
            "recommendations": "Specific recommendations based on the knowledge"
        }
        ```
        """)
    
    def _mock_knowledge_base(self):
        """
        Create a mock knowledge base for development purposes.
        In a real implementation, this would be replaced with a vector database or API.
        
        Returns:
            A mock knowledge base object
        """
        class MockKnowledgeBase:
            def search(self, query, domain):
                # Simulate knowledge retrieval
                domain_knowledge = {
                    "mechanical": {
                        "materials": "Information about mechanical engineering materials...",
                        "processes": "Information about manufacturing processes..."
                    },
                    "electrical": {
                        "circuits": "Information about electrical circuits...",
                        "components": "Information about electrical components..."
                    },
                    "civil": {
                        "structures": "Information about civil engineering structures...",
                        "codes": "Information about building codes..."
                    },
                    "aerospace": {
                        "aerodynamics": "Information about aerodynamics...",
                        "safety": "Information about aerospace safety standards..."
                    },
                    "cad": {
                        "modeling": "Information about CAD modeling techniques...",
                        "organization": "Information about CAD file organization..."
                    }
                }
                
                standards = {
                    "mechanical": [
                        {"standard_name": "ASME Y14.5", "description": "Dimensioning and Tolerancing"},
                        {"standard_name": "ISO 9001", "description": "Quality Management Systems"}
                    ],
                    "electrical": [
                        {"standard_name": "IEC 60601", "description": "Medical Electrical Equipment"},
                        {"standard_name": "IEEE 1584", "description": "Arc Flash Hazard Calculations"}
                    ],
                    "civil": [
                        {"standard_name": "ACI 318", "description": "Building Code Requirements for Structural Concrete"},
                        {"standard_name": "ASCE 7", "description": "Minimum Design Loads for Buildings"}
                    ],
                    "aerospace": [
                        {"standard_name": "AS9100", "description": "Quality Management Systems - Aerospace"},
                        {"standard_name": "FAR Part 25", "description": "Airworthiness Standards: Transport Category Aircraft"}
                    ],
                    "cad": [
                        {"standard_name": "STEP (ISO 10303)", "description": "Standard for Exchange of Product Data"},
                        {"standard_name": "ASME Y14.41", "description": "Digital Product Definition Data Practices"}
                    ]
                }
                
                best_practices = {
                    "mechanical": [
                        "Use appropriate safety factors in design calculations",
                        "Consider manufacturing constraints during design"
                    ],
                    "electrical": [
                        "Implement proper grounding techniques",
                        "Use standardized component libraries"
                    ],
                    "civil": [
                        "Account for environmental loads in structural design",
                        "Follow local building codes and regulations"
                    ],
                    "aerospace": [
                        "Implement redundancy in critical systems",
                        "Follow strict quality control procedures"
                    ],
                    "cad": [
                        "Use parametric modeling for design flexibility",
                        "Maintain consistent naming conventions for files and features"
                    ]
                }
                
                # Return mock data based on domain
                return {
                    "domain_knowledge": domain_knowledge.get(domain, {}).get(query.lower(), "No specific knowledge found"),
                    "standards": standards.get(domain, []),
                    "best_practices": best_practices.get(domain, []),
                    "references": [f"Reference for {domain} - {query}", "General engineering handbook"]
                }
        
        return MockKnowledgeBase()
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current state and provide knowledge.
        
        Args:
            state: The current workflow state
            
        Returns:
            Updated workflow state
        """
        # Extract the knowledge task from the state
        knowledge_tasks = state["knowledge_context"].get("tasks", [])
        if not knowledge_tasks:
            state["errors"].append("No knowledge tasks found for Knowledge Agent")
            return state
        
        # Process the most recent task
        current_task = knowledge_tasks[-1]
        
        # Extract domain and query from the task
        # In a real implementation, this would be more sophisticated
        task_parts = current_task.split(":")
        domain = "cad"  # Default domain
        query = current_task
        
        if len(task_parts) > 1:
            domain = task_parts[0].strip().lower()
            query = task_parts[1].strip()
            
            # Map domain to one of our supported domains
            domain_mapping = {
                "mechanical": "mechanical",
                "mech": "mechanical",
                "electrical": "electrical",
                "elec": "electrical",
                "civil": "civil",
                "aerospace": "aerospace",
                "aero": "aerospace",
                "cad": "cad",
                "design": "cad"
            }
            domain = domain_mapping.get(domain, "cad")
        
        # Process with the LLM
        response = self.chain.invoke({
            "task": current_task,
            "knowledge_context": json.dumps(state["knowledge_context"]),
            "domain": domain,
            "query": query
        })
        
        # Extract the JSON response
        response_content = response.content
        json_start = response_content.find('```json') + 7
        json_end = response_content.find('```', json_start)
        json_str = response_content[json_start:json_end].strip()
        
        try:
            knowledge_response = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            knowledge_response = {
                "domain_knowledge": "Failed to parse JSON response",
                "standards": [],
                "best_practices": [],
                "references": [],
                "recommendations": "Error in Knowledge agent response"
            }
            state["errors"].append("Knowledge agent produced invalid JSON response")
        
        # Update the state with the results
        updated_state = state.copy()
        updated_state["knowledge_context"] = {
            **updated_state["knowledge_context"],
            "domain": domain,
            "query": query,
            "domain_knowledge": knowledge_response["domain_knowledge"],
            "standards": knowledge_response["standards"],
            "best_practices": knowledge_response["best_practices"],
            "references": knowledge_response["references"],
            "recommendations": knowledge_response["recommendations"]
        }
        
        # Remove the processed task
        updated_state["knowledge_context"]["tasks"] = knowledge_tasks[:-1]
        
        # Add message to the state
        updated_state["messages"].append({
            "role": "knowledge_agent",
            "content": f"Knowledge Response ({domain}):\n\n{knowledge_response['domain_knowledge']}\n\nBest Practices:\n- " + 
                      "\n- ".join(knowledge_response['best_practices']) + 
                      f"\n\nRecommendations: {knowledge_response['recommendations']}"
        })
        
        # Set next agent back to coordinator
        updated_state["next_agent"] = "coordinator_agent"
        
        return updated_state
