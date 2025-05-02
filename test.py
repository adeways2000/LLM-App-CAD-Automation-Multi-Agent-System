"""
Test Module for Company CAD Automation Multi-Agent System

This module provides test cases and validation for the CAD automation
multi-agent system, ensuring all components work correctly together.
"""
import os
from dotenv import load_dotenv
import unittest
import json
import sys
from typing import Dict, Any

# Import the components to test
from main import CADAutomationApp
from agents.coordinator_agent import CoordinatorAgent
from agents.cad_agent import CADAgent
from agents.design_agent import DesignAgent
from agents.analysis_agent import AnalysisAgent
from agents.knowledge_agent import KnowledgeAgent
from integration import CompanyIntegration

class TestCADAutomationSystem(unittest.TestCase):
    """
    Test cases for the CAD Automation System.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = CADAutomationApp()
        self.integration = CompanyIntegration()
        
        # Sample test inputs
        self.test_inputs = [
            "Design a simple bracket that can support 50kg of weight",
            "Create a gear with 24 teeth and a diameter of 100mm",
            "Analyze the structural integrity of a beam under 1000N load",
            "What are the best practices for designing parts for CNC machining?",
            "Optimize my current design to reduce weight while maintaining strength"
        ]
    
    def test_coordinator_agent(self):
        """Test the Coordinator Agent."""
        coordinator = CoordinatorAgent()
        
        # Test with a simple input
        state = {
            "user_input": "Design a simple bracket",
            "current_stage": "initial",
            "cad_model_state": {},
            "design_state": {},
            "analysis_state": {},
            "knowledge_context": {},
            "messages": [],
            "errors": [],
            "next_agent": None
        }
        
        result = coordinator.process(state)
        
        # Verify the coordinator has routed to an agent
        self.assertIsNotNone(result["next_agent"])
        self.assertIn("messages", result)
        self.assertTrue(len(result["messages"]) > 0)
    
    def test_cad_agent(self):
        """Test the CAD Agent."""
        cad_agent = CADAgent()
        
        # Test with a CAD task
        state = {
            "user_input": "Create a gear with 24 teeth",
            "current_stage": "delegated_to_cad_agent",
            "cad_model_state": {
                "tasks": ["Create a gear with 24 teeth and a diameter of 100mm"]
            },
            "design_state": {
                "constraints": {
                    "min_tooth_thickness": 2.5
                }
            },
            "analysis_state": {},
            "knowledge_context": {},
            "messages": [],
            "errors": [],
            "next_agent": "cad_agent"
        }
        
        result = cad_agent.process(state)
        
        # Verify the CAD agent has processed the task
        self.assertEqual(result["next_agent"], "coordinator_agent")
        self.assertIn("messages", result)
        self.assertTrue(len(result["messages"]) > 0)
        self.assertIn("last_operations", result["cad_model_state"])
    
    def test_design_agent(self):
        """Test the Design Agent."""
        design_agent = DesignAgent()
        
        # Test with a design task
        state = {
            "user_input": "Design a bracket that can support 50kg",
            "current_stage": "delegated_to_design_agent",
            "cad_model_state": {},
            "design_state": {
                "tasks": ["Design a bracket that can support 50kg of weight"]
            },
            "analysis_state": {},
            "knowledge_context": {},
            "messages": [],
            "errors": [],
            "next_agent": "design_agent"
        }
        
        result = design_agent.process(state)
        
        # Verify the design agent has processed the task
        self.assertEqual(result["next_agent"], "coordinator_agent")
        self.assertIn("messages", result)
        self.assertTrue(len(result["messages"]) > 0)
        self.assertIn("constraints", result["design_state"])
        self.assertIn("parameters", result["design_state"])
    
    def test_analysis_agent(self):
        """Test the Analysis Agent."""
        analysis_agent = AnalysisAgent()
        
        # Test with an analysis task
        state = {
            "user_input": "Analyze the structural integrity of a beam",
            "current_stage": "delegated_to_analysis_agent",
            "cad_model_state": {
                "elements": {
                    "solids": 1
                }
            },
            "design_state": {
                "parameters": {
                    "length": 500,
                    "width": 50,
                    "height": 25,
                    "material": "steel"
                }
            },
            "analysis_state": {
                "tasks": ["Analyze the structural integrity of a beam under 1000N load"]
            },
            "knowledge_context": {},
            "messages": [],
            "errors": [],
            "next_agent": "analysis_agent"
        }
        
        result = analysis_agent.process(state)
        
        # Verify the analysis agent has processed the task
        self.assertEqual(result["next_agent"], "coordinator_agent")
        self.assertIn("messages", result)
        self.assertTrue(len(result["messages"]) > 0)
        self.assertIn("last_analysis", result["analysis_state"])
    
    def test_knowledge_agent(self):
        """Test the Knowledge Agent."""
        knowledge_agent = KnowledgeAgent()
        
        # Test with a knowledge task
        state = {
            "user_input": "What are the best practices for CNC machining?",
            "current_stage": "delegated_to_knowledge_agent",
            "cad_model_state": {},
            "design_state": {},
            "analysis_state": {},
            "knowledge_context": {
                "tasks": ["mechanical: What are the best practices for designing parts for CNC machining?"]
            },
            "messages": [],
            "errors": [],
            "next_agent": "knowledge_agent"
        }
        
        result = knowledge_agent.process(state)
        
        # Verify the knowledge agent has processed the task
        self.assertEqual(result["next_agent"], "coordinator_agent")
        self.assertIn("messages", result)
        self.assertTrue(len(result["messages"]) > 0)
        self.assertIn("domain_knowledge", result["knowledge_context"])
        self.assertIn("best_practices", result["knowledge_context"])
    
    def test_end_to_end_workflow(self):
        """Test the end-to-end workflow with the CAD Automation App."""
        for test_input in self.test_inputs:
            result = self.app.process_request(test_input)
            
            # Verify the workflow completed successfully
            self.assertIn("messages", result)
            self.assertTrue(len(result["messages"]) > 0)
            self.assertNotIn("error", result["current_stage"].lower())
    
    def test_integration(self):
        """Test the integration with Company platform."""
        for test_input in self.test_inputs:
            result = self.integration.process_request(test_input)
            
            # Verify the integration worked correctly
            self.assertIn("messages", result)
            self.assertTrue(len(result["messages"]) > 0)
            
            # Check for enhanced data from Company platform
            if "cad_model_state" in result and result["cad_model_state"]:
                if "visualization_url" in result["cad_model_state"]:
                    self.assertTrue(result["cad_model_state"]["visualization_url"].startswith("https://"))
            
            if "analysis_state" in result and result["analysis_state"]:
                if "last_analysis" in result["analysis_state"] and "visualization_url" in result["analysis_state"]["last_analysis"]:
                    self.assertTrue(result["analysis_state"]["last_analysis"]["visualization_url"].startswith("https://"))

def run_tests():
    """Run all tests."""
    unittest.main()

if __name__ == "__main__":
    run_tests()
