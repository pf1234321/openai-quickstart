from langchain_core.messages import AIMessage, HumanMessage
from typing import Annotated
from langgraph.graph.message import add_messages
from prompts import writer, reflect

# 定义状态类，使用TypedDict以保存消息
class State(dict):
    messages: Annotated[list, add_messages]  # 使用注解确保消息列表使用add_messages方法处理

# 这段代码同样使用了 Python 的类型注解功能，具体来说：
# - `messages` 是一个变量或属性的名称。
# - `Annotated[list, add_messages]` 是对 `messages` 的类型注解。
# 详细解释如下：
# 1. **`list`**:
#    - `list` 是一个内置的 Python 类型，表示一个可变的有序集合，通常用来存储多个元素。
# 2. **`Annotated[...]`**:
#    - `Annotated` 是一个类型注解工具，用于在类型上添加额外的元数据。
#    - `Annotated[list, add_messages]` 表示 `messages` 是一个 `list` 类型的列表，并且附加了一个 `add_messages` 的元数据。
# 3. **`add_messages`**:
#    - `add_messages` 是一个标识符，可能是某个函数、方法或常量的名称。
#    - 在这里，`add_messages` 作为元数据被附加到 `list` 上，可能是为了提供某种特定的语义或行为说明。
# 总结起来，这行代码的意思是：`messages` 是一个包含多个元素的列表，并且附加了 `add_messages` 这个元数据，
# 可能用于指示某些特定的操作或行为。例如，`add_messages` 可能是一个函数，用于向 `messages` 列表中添加新的消息。

# 异步生成节点函数：生成内容（如作文）
# 输入状态，输出包含新生成消息的状态
async def generation_node(state: State) -> State:
    # 调用生成器(writer)，并将消息存储到新的状态中返回
    new_message = await writer.ainvoke(state['messages'])
    # new_message = writer.invoke(state['messages'])
    return {"messages": state['messages'] + [new_message]}

# 异步反思节点函数：对生成的内容进行反思和反馈
# 输入状态，输出带有反思反馈的状态
async def reflection_node(state: State) -> State:
    # 创建一个消息类型映射，ai消息映射为HumanMessage，human消息映射为AIMessage
    cls_map = {"ai": HumanMessage, "human": AIMessage}

    # 处理消息，保持用户的原始请求（第一个消息），转换其余消息的类型
    translated = [state['messages'][0]] + [
        cls_map[msg.type](content=msg.content) for msg in state['messages'][1:]
    ]

    # 调用反思器(reflect)，将转换后的消息传入，获取反思结果
    res = await reflect.ainvoke(translated)

    # 返回新的状态，其中包含反思后的消息
    return {"messages": state['messages'] + [HumanMessage(content=res.content)]}
