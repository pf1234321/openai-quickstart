from langgraph.graph import StateGraph, START, END
from nodes import generation_node, reflection_node, State
from langgraph.graph import END, StateGraph, START  # 导入状态图的相关常量和类
# 定义条件函数，决定是否继续反思过程
# 如果消息数量超过6条，则终止流程
def should_continue(state):
    if len(state["messages"]) > 2:
        return END  # 达到条件时，流程结束
    return "reflect"  # 否则继续进入反思节点

# 创建状态图，传入初始状态结构
def build_graph():
    builder = StateGraph(State)

    # 在状态图中添加"writer"节点，节点负责生成内容
    builder.add_node("writer", generation_node)

    # 在状态图中添加"reflect"节点，节点负责生成反思反馈
    builder.add_node("reflect", reflection_node)

    # 定义起始状态到"writer"节点的边，从起点开始调用生成器
    builder.add_edge(START, "writer")

    # 在"writer"节点和"reflect"节点之间添加条件边
    # 判断是否需要继续反思，或者结束
    builder.add_conditional_edges("writer", should_continue)

    # 添加从"reflect"节点回到"writer"节点的边，进行反复的生成-反思循环
    builder.add_edge("reflect", "writer")

    # 创建内存保存机制，允许在流程中保存中间状态和检查点
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()

    # 编译状态图，使用检查点机制
    graph = builder.compile(checkpointer=memory)
    return graph
