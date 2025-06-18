import os
import uuid
from dotenv import load_dotenv
import asyncio
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import gradio as gr

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Must provide OPENAI_API_KEY environment variable")


llm = init_chat_model(model="gpt-4.1-mini", model_provider="openai")

async def chatbot():
    """Create a LangGraph React agent with tools."""
    mcp_client = MultiServerMCPClient(
        {
            "ShoppingList": {
                "url": "http://localhost:8000/mcp",
                "transport": "sse",
            }
        }
    )
    tools = await mcp_client.get_tools()
    prompt = """
    You're a helpful assistant that let's users manage their shopping list using the ShoppingList tool.
    """
    
    # Create the React agent
    agent = create_react_agent(llm, tools, prompt=prompt)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    

    async def chat_with_agent(message, history):
        """Chat function that interfaces with the LangGraph agent."""
        
        # Prepare the input for the agent
        agent_input = {
            "messages": history + [{"role": "user", "content": message}]
        }
        
        # Run the agent
        result = await agent.ainvoke(agent_input, config)
        
        agent_response = result["messages"][-1].content
        return agent_response

    """Create and return the Gradio chat interface."""
    # Create the chat interface
    chat_interface = gr.ChatInterface(
        fn=chat_with_agent,
        title="🤖 Shopping List Agent",
        description="Chat with an AI agent that can manage your shopping list.",
        examples=[
            "I need to buy a watermelon",
            "What's in my shopping list?",
            "Let's add spaghetti and tomato sauce",
            "I just bought the watermelon",
            "Remove the tomato sauce",
            "I need an extra spaghetti",
        ],
        type="messages", 
    )
    chat_interface.launch()

if __name__ == "__main__":
    asyncio.run(chatbot())
