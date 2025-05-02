"""
User Interface for Company CAD Automation Multi-Agent System

This module implements a Streamlit-based user interface for the CAD automation
multi-agent system, allowing users to interact with the system through natural language.
"""
import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the CAD automation application
from main import CADAutomationApp

def initialize_session_state():
    """Initialize the Streamlit session state with default values."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
     # Initialize workflow state with proper typing
    workflow_state_default = {
        "user_input": "",
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
        "messages": [],
        "errors": [],
        "next_agent": "coordinator_agent"
    }
    
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = workflow_state_default
    
    if "app" not in st.session_state:
        try:
            st.session_state.app = CADAutomationApp()
        except Exception as e:
            st.error(f"Failed to initialize application: {str(e)}")
            st.stop()

def display_header():
    """Display the application header and description."""
    st.title("🔧 Company CAD Automation Assistant")
    st.markdown("""
    **Multi-Agent CAD Design System**  
    Describe your CAD tasks in natural language, and our AI agents will:
    - 🛠️ Create and modify 3D models
    - 📐 Perform engineering analysis
    - 💡 Provide design recommendations
    - 📚 Suggest relevant standards
    """)

def handle_user_input():
    """Handle user input and process it through the multi-agent system."""
    if prompt := st.chat_input("Describe your CAD task..."):
        # Clear previous errors
        st.session_state.workflow_state["errors"] = []
        
        try:
            with st.spinner("🚀 Processing your request..."):
                result = st.session_state.app.process_request(prompt)
                st.session_state.workflow_state = result
                
                # Update chat history
                for message in result["messages"]:
                    if message not in st.session_state.messages:
                        st.session_state.messages.append(message)
                        
        except Exception as e:
            st.session_state.workflow_state["errors"].append(str(e))
            st.error(f"Processing error: {str(e)}")

def display_chat_message(message: dict):
    """Display a single chat message with optional visualization."""
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Handle visualizations
        visuals = []
        if message["role"] == "analysis_agent":
            visuals = st.session_state.workflow_state["analysis_state"].get("visualizations", [])
        elif message["role"] == "cad_agent":
            visuals = st.session_state.workflow_state["cad_model_state"].get("visualizations", [])
        
        for viz in visuals:
            if viz.get("type") == "image":
                st.image(viz["url"], caption=viz.get("caption"))

def display_chat_history():
    """Display the chat history between the user and the agents."""
    for message in st.session_state.messages:
        display_chat_message(message)

def display_workflow_status():
    """Display the current workflow status in the sidebar."""
    st.sidebar.header("Workflow Dashboard")
    
    # Status indicators
    stage = st.session_state.workflow_state["current_stage"]
    status_color = {
        "initial": "gray",
        "processing": "blue",
        "completed": "green",
        "error": "red"
    }.get(stage, "gray")
    
    st.sidebar.markdown(f"**Current Stage:** <span style='color:{status_color}'>➤ {stage.capitalize()}</span>", 
                       unsafe_allow_html=True)
    
    # Display error if any
    if st.session_state.workflow_state["errors"]:
        st.sidebar.error("## Errors")
        for error in st.session_state.workflow_state["errors"]:
            st.sidebar.error(f"- {error}")

def display_example_prompts():
    """Display example prompts that users can try."""
    st.sidebar.header("💡 Example Prompts")
    examples = [
        ("Design a planetary gear system", "mechanical"),
        ("Analyze stress on bracket under 200N load", "analysis"),
        ("Optimize part for 3D printing", "manufacturing"),
        ("Suggest materials for high-temperature use", "materials")
    ]
    
    for text, category in examples:
        if st.sidebar.button(text, help=f"Category: {category}"):
            st.session_state.messages.append({"role": "user", "content": text})
            try:
                with st.spinner("Processing example request..."):
                    result = st.session_state.app.process_request(text)
                    st.session_state.workflow_state = result
                    st.rerun()
            except Exception as e:
                st.error(f"Error processing example: {str(e)}")

def main():
    """Main function to run the Streamlit application."""
    # Configure page settings
    st.set_page_config(
        page_title="Company CAD Assistant",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize application state
    initialize_session_state()
    
    # Main interface layout
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        display_header()
        display_chat_history()
        handle_user_input()
    
    with col2:
        st.header("Design Visualization")
        if viz_url := st.session_state.workflow_state["cad_model_state"].get("visualization_url"):
            st.image(viz_url, use_column_width=True)
        elif analysis_viz := st.session_state.workflow_state["analysis_state"].get("visualization"):
            st.image(analysis_viz["url"], caption=analysis_viz.get("caption"))
        else:
            st.info("No visualization available yet. Describe a CAD task to get started!")
    
    # Sidebar components
    with st.sidebar:
        display_workflow_status()
        display_example_prompts()
        st.markdown("---")
        st.markdown("**CAD System Status**")
        st.json({
            "CAD Elements": len(st.session_state.workflow_state["cad_model_state"]["elements"]),
            "Active Design Constraints": len(st.session_state.workflow_state["design_state"]["constraints"]),
            "Pending Analyses": len(st.session_state.workflow_state["analysis_state"]["results"])
        })

if __name__ == "__main__":
    main()