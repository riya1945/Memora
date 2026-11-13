from langchain_core.messages import HumanMessage

from memora.tools.tools import (
    search_project,
    get_experiment,
    search_memory,
    save_memory,
    list_categories,
    read_project_file,
    propose_edit,
    run_project_tests
)
from memora.context.budget import ContextBudget
from memora.context.tokenizer import TokenCounter
from memora.context.manager import ContextManager
from memora.tools.tools import service

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_ollama import ChatOllama


context_budget = ContextBudget(
    maximum=4096,
    reserved=512
)

token_counter = TokenCounter()

context_manager = ContextManager(
    budget=context_budget,
    token_counter=token_counter,
    retriever=service.retriever
)

llm = ChatOllama(
    model="qwen3:4b",temperature=0,num_ctx=4096
)

tools = [
    search_project,
    get_experiment,
    search_memory,
    save_memory,
    list_categories,
    read_project_file,
    propose_edit,
    run_project_tests
]

tool_node=ToolNode(tools)


llm_with_tools = llm.bind_tools(tools)

def call_model(state:MessagesState):
    response=llm_with_tools.invoke(state["messages"])
    print("TOOL CALLS:", response.tool_calls)
    return {"messages":[response]}

stategraph=StateGraph(MessagesState)

stategraph.add_node("model",call_model)
stategraph.add_node("tools",tool_node)
stategraph.add_edge(START,"model")
stategraph.add_conditional_edges("model",tools_condition)
stategraph.add_edge("tools","model")

graph=stategraph.compile() # prepares the graph to be executed

tool_map = {
    "search_project": search_project,
    "get_experiment": get_experiment,
    "search_memory": search_memory,
    "save_memory": save_memory,
    "list_categories":list_categories
}


def run_agent(user_input,mode="everyday",project_root:str |None=None):
    if mode=="code":
        category="codebase"
        exclude_category=None
    else:
        category=None
        exclude_category="codebase"    
    selected_context = context_manager.select_context(user_input,category=category,exclude_category=exclude_category)
    formatted_context = context_manager.format_context(selected_context)

    if formatted_context:
        prompt = f"""
{formatted_context}

Current user request:
{user_input}
"""
    else:
        prompt = user_input

    user_message = HumanMessage(content=prompt)
    content=graph.invoke({"messages": [user_message]},
                         config={
                             "configurable":{
                                 "project_root":project_root
                             }
                         })
    return content["messages"][-1].content

