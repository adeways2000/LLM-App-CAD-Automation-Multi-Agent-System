# LLM-App-CAD-Automation-Multi-Agent-System
 An LLM App for Automated 3D CAD Workflow leverages LangGraph to create a multi-agent system that enhances low-code engineering platforms with advanced AI capabilities for CAD automation, data processing, and engineering workflows.

The system follows a hierarchical multi-agent architecture using LangGraph, with a central coordinator agent managing specialized agents for different aspects of the CAD workflow:




## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Pip package manager

### Installation Steps

1. Clone the repository:
   ```bash
   git clone 
   cd cad-automation-agents
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Create a .env file with the following variables
   OPENAI_API_KEY=your_openai_api_key
   COMPANY_API_KEY=your_COMPANY_api_key
   COMPANY_BASE_URL=https://api.company.io
   ```

## Usage Guide

### Running the Application

1. Start the application:
   ```bash
   streamlit run ui.py
   ```

2. Access the application in your web browser at `http://localhost:8501`
