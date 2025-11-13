from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
import operator
import requests
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_logs = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load from current directory
    load_dotenv(".env")
    load_dotenv("/Users/kristina/python/deploying-ai/05_src/.secrets")
    
    # Check if API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        _logs.info("OpenAI API key loaded successfully")
        _logs.info(f"API key starts with: {api_key[:10]}...")
    else:
        _logs.error("OPENAI_API_KEY not found in environment variables")
        _logs.info("Current directory: " + os.getcwd())
        _logs.info(".secrets file exists: " + str(os.path.exists(".secrets")))
        
except ImportError:
    _logs.warning("python-dotenv not installed")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        _logs.error("OPENAI_API_KEY not found and dotenv not available")

# ---- Tools ---- #

@tool
def get_threat_info(query: str):
    """Returns relevant information from the cyber-physical threat dataset"""
    url = "http://127.0.0.1:8002/search"
    
    try:
        response = requests.get(url, params={"q": query}, timeout=10)
        response.raise_for_status()
        results = response.json()

        if results and isinstance(results, list):
            facts = "\n".join([f"{i+1}. {item.get('text', 'No text')} (score: {item.get('score', 0)})"
                               for i, item in enumerate(results)])
            return f"Top relevant results for '{query}':\n{facts}"
        else:
            return f"No results found for '{query}'"

    except requests.exceptions.RequestException as e:
        return f"Error connecting to semantic search service: {e}"

@tool
def get_prevention_tips():
    """Returns general best practices for preventing cyber-physical attacks."""
    return (
        "To prevent cyber-physical attacks:\n"
        "1. Implement strong authentication for IoT devices.\n"
        "2. Isolate OT networks from IT systems.\n"
        "3. Regularly patch firmware and software.\n"
        "4. Monitor network traffic for anomalies.\n"
        "5. Train operators to identify suspicious behavior."
    )

# Bind LLM + Tools
def get_model_with_tools():
    try:
        _logs.info("Initializing chat model...")
        
        # Check API key again
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            _logs.error("No OpenAI API key found")
            raise ValueError("OpenAI API key not found")
        
        # Use ChatOpenAI directly for better error handling
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=api_key
        )
        
        tools = [get_threat_info, get_prevention_tips]
        model_with_tools = model.bind_tools(tools)
        _logs.info("Model with tools initialized successfully")
        return model_with_tools
        
    except Exception as e:
        _logs.error(f"Failed to initialize model: {e}")
        # Return a placeholder model
        class PlaceholderModel:
            def invoke(self, messages):
                from langchain_core.messages import AIMessage
                return AIMessage(content="Chat agent is not available. Please check the server logs for details.")
        return PlaceholderModel()

# ---- Define LLM State Machine ---- #
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""
    model_with_tools = get_model_with_tools()
    
    system_message = SystemMessage(
        content="You are a cybersecurity assistant. Help the user understand cyber-physical threats using the dataset, and recommend best practices for protection."
    )
    
    all_messages = [system_message] + state["messages"]
    
    try:
        response = model_with_tools.invoke(all_messages)
        return {
            "messages": [response],
            "llm_calls": state.get('llm_calls', 0) + 1
        }
    except Exception as e:
        _logs.error(f"Error in LLM call: {e}")
        from langchain_core.messages import AIMessage
        return {
            "messages": [AIMessage(content=f"Error processing request: {str(e)}")],
            "llm_calls": state.get('llm_calls', 0) + 1
        }

def tool_node(state: dict):
    """Perform the tool call"""
    tools = [get_threat_info, get_prevention_tips]
    tools_by_name = {tool.name: tool for tool in tools}

    result = []
    last_message = state["messages"][-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    
    return {"messages": result}

def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop"""
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tool_node"
    return END

# Build Agent
def get_threat_chat_agent():
    """Returns the cyber-physical threat chat agent"""
    try:
        _logs.info("Building threat chat agent...")
        agent_builder = StateGraph(MessagesState)
        agent_builder.add_node("llm_call", llm_call)
        agent_builder.add_node("tool_node", tool_node)

        agent_builder.add_edge(START, "llm_call")
        agent_builder.add_conditional_edges("llm_call", should_continue, {"tool_node": "tool_node", END: END})
        agent_builder.add_edge("tool_node", "llm_call")
        
        agent = agent_builder.compile()
        _logs.info("Agent built successfully")
        return agent
    except Exception as e:
        _logs.error(f"Error building agent: {e}")
        return None
