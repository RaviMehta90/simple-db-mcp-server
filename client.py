import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools

# LangChain utility to initialize a chat model (in this case, Gemini)
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# Set up logging
logging.basicConfig(
    filename="agent_actions.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# MCP server parameters
server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)

MAX_HISTORY_MESSAGES = 20  # 10 pairs of user+assistant

GOOGLE_API_KEY = "<YOUR GEMINI API KEY>"

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            # Option 1, Using Gemini 2.0 Flash model (Very Fast)
            # llm = init_chat_model("google_genai:gemini-2.0-flash")
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.3,
                google_api_key=GOOGLE_API_KEY  # Make sure this is loaded from .env or defined earlier
            )

            # Option 2, Using Ollama Local Model (Super Slow, since they run locally)
            # llm = ChatOllama(model="qwen3:14b", temperature=0)

            agent = create_react_agent(llm, tools)

            print("\n💬 eCommerce Assistant is ready! Type your message (or 'exit' to quit):\n")
            messages = []

            while True:
                user_input = input("\n\U0001f9d1 You: ").strip()
                logging.info("USER: %s", user_input)
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\U0001f44b Assistant: Goodbye!")
                    break

                # Add user message
                user_message = HumanMessage(content=user_input)
                messages.append(user_message)

                # Keep only the last 20 messages
                messages = messages[-MAX_HISTORY_MESSAGES:]

                try:
                    response = await agent.ainvoke({"messages": messages})
                    response_messages = response["messages"]
                    response_messages[-1].pretty_print() # Print the AI message
                    
                    messages.extend(response_messages)

                    # for m in response_messages:
                    #     print(m)
                    #     print(type(m))
                    #     m.pretty_print()


                except Exception as e:
                    print("❌ Error:", e)
                    logging.error("Exception occurred: %s", str(e))


if __name__ == "__main__":
    asyncio.run(run_agent())
