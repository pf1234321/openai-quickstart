import io
import os
from typing import Annotated
from typing import Literal

# 你可以使用 get_graph 方法来可视化图，并结合 draw 方法（如 draw_ascii 或 draw_png）
from PIL import Image
from dotenv import load_dotenv, find_dotenv
from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI
from langfuse.decorators import observe
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from jk.lesson09.BasicToolNode import BasicToolNode

_ = load_dotenv(find_dotenv())
os.environ["TAVILY_API_KEY"] = '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'


# 定义状态类型，继承自 TypedDict，并使用 add_messages 函数将消息追加到现有列表
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 创建一个状态图对象，传入状态定义  @observe(as_type="generation")
graph_builder = StateGraph(State)


# 定义路由函数，检查工具调用
def route_tools(
        state: State,
) -> Literal["tools", "__end__"]:
    """
    使用条件边来检查最后一条消息中是否有工具调用。

    参数:
    state: 状态字典或消息列表，用于存储当前对话的状态和消息。

    返回:
    如果最后一条消息包含工具调用，返回 "tools" 节点，表示需要执行工具调用；
    否则返回 "__end__"，表示直接结束流程。
    """
    # 检查状态是否是列表类型（即消息列表），取最后一条 AI 消息
    if isinstance(state, list):
        ai_message = state[-1]
    # 否则从状态字典中获取 "messages" 键，取最后一条消息
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    # 如果没有找到消息，则抛出异常
    else:
        raise ValueError(f"输入状态中未找到消息: {state}")

    # 检查最后一条消息是否有工具调用请求
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"  # 如果有工具调用请求，返回 "tools" 节点
    return "__end__"  # 否则返回 "__end__"，流程结束


# =====================================================================
# 初始化一个 GPT-4o-mini 模型
chat_model = ChatOpenAI(model="gpt-4o-mini")

tool = TavilySearchResults(max_results=2)
tools = [tool]

llm_with_tools = chat_model.bind_tools(tools)


# 绑定天气查询工具和翻译工具
# bound_model = chat_model.bind(
#     tools={
#         "weather": tool,
#         "translate": tool
#     }
# )


# llm_with_tools = chat_model.bind(
#     tools={
#         "tool": tool
#     }
# )


# 定义聊天机器人的节点函数，接收当前状态并返回更新的消息列表
@observe(name="generation")
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# 指定从 START 节点开始，进入聊天机器人节点
graph_builder.add_edge(START, "chatbot")
graph_builder.add_node("chatbot", chatbot)

tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
# 添加条件边，判断是否需要调用工具
graph_builder.add_conditional_edges(
    "chatbot",  # 从聊天机器人节点开始
    route_tools,  # 路由函数，决定下一个节点
    {
        "tools": "tools",
        "__end__": "__end__"
    },  # 定义条件的输出，工具调用走 "tools"，否则走 "__end__"
)



# graph_builder.add_conditional_edges(
#     source="chatbot",  # 从聊天机器人节点开始
#     condition_func=route_tools,  # 路由函数，决定下一个节点
#     mapping={
#         "tools": "tools",
#         "__end__": "__end__"
#     }  # 定义条件的输出，工具调用走 "tools"，否则走 "__end__"
# )

# 当工具调用完成后，返回到聊天机器人节点以继续对话
graph_builder.add_edge("tools", "chatbot")



# 编译状态图并生成可执行图对象
graph = graph_builder.compile()

try:
    # 获取图像数据
    image_data = graph.get_graph().draw_mermaid_png()
    # 将图像数据转换为 PIL 图像对象
    image = Image.open(io.BytesIO(image_data))
    # 保存图像到本地文件
    image.save('output.png')
except Exception:
    pass

# 开始一个简单的聊天循环
while True:
    # 获取用户输入
    user_input = input("User: ")

    # 可以随时通过输入 "quit"、"exit" 或 "q" 退出聊天循环
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")  # 打印告别信息
        break  # 结束循环，退出聊天

    # 将每次用户输入的内容传递给 graph.stream，用于聊天机器人状态处理
    # "messages": ("user", user_input) 表示传递的消息是用户输入的内容
    for event in graph.stream({"messages": ("user", user_input)}):
        print(f"event==={event}")
        # 遍历每个事件的值
        for value in event.values():
            # print(value)
            # 打印输出 chatbot 生成的最新消息
            print("Assistant:", value["messages"][-1].content)
