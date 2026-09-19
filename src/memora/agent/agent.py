import json
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, ToolMessage

from memora.tools.tools import (
    search_project,
    get_experiment,
    search_memory,
    save_memory
)


llm1 = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    task="text-generation"
)

llm = ChatHuggingFace(llm=llm1)



tools = [
    search_project,
    get_experiment,
    search_memory,
    save_memory
]

llm_with_tools = llm.bind_tools(tools)

tool_map = {
    "search_project": search_project,
    "get_experiment": get_experiment,
    "search_memory": search_memory,
    "save_memory": save_memory
}




def run_agent(user_input):
    user_message = HumanMessage(content=user_input)

    messages = [user_message]

    response = llm_with_tools.invoke(messages)
    messages.append(response)

    while response.tool_calls:

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            tool = tool_map[tool_name]

            tool_result = tool.invoke(tool_args)

            tool_message = ToolMessage(
                content=json.dumps(tool_result),
                tool_call_id=tool_call["id"]
            )

            messages.append(tool_message)

        response = llm_with_tools.invoke(messages)
        messages.append(response)

    return response.content


