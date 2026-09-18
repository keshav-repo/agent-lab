import asyncio
import os

from agents import Agent, WebSearchTool, trace, Runner, function_tool
from agents.model_settings import ModelSettings
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from Models.LearningEntity import LearningEntity

model = "gpt-5.4-mini"
INSTRUCTIONS = """
You are a categorisation agent. Your task is to categorise the given text into a hierarchy
"""

category_agent = Agent(
    name="Categorisation Agent",
    instructions=INSTRUCTIONS,
    output_type=LearningEntity,
    handoff_description="This agent is responsible for categorising text into a hierarchy of categories, subcategories, topics, subtopics, and concepts. It uses a combination of machine learning models and rule-based approaches to accurately classify the text based on its content.",
)
