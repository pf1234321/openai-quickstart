from IPython.display import Markdown, display
from langchain_core.messages import HumanMessage
from graph_builder import build_graph
import asyncio

# 定义装饰器，记录函数调用次数
def track_steps(func):
    step_counter = {'count': 0}  # 用于记录调用次数

    def wrapper(event, *args, **kwargs):
        # 增加调用次数
        step_counter['count'] += 1
        # 在函数调用之前打印 step
        display(Markdown(f"## Round {step_counter['count']}"))
        # 调用原始函数
        return func(event, *args, **kwargs)

    return wrapper


# 使用装饰器装饰 pretty_print_event_markdown 函数
@track_steps
def pretty_print_event_markdown(event):
    writer_file_path = 'writer.md'
    reflect_file_path = 'reflect.md'
    # default_file_path = 'output.md'

    # 如果是生成写作部分
    if 'writer' in event:
        generate_md = "#### 写作生成:\n"
        for message in event['writer']['messages']:
            generate_md += f"- {message.content}\n"

        with open(writer_file_path, 'a') as f:  # 使用 'a' 模式追加内容
            f.write(generate_md + "\n")
        # display(Markdown(generate_md))

    # 如果是反思评论部分
    if 'reflect' in event:
        reflect_md = "#### 评论反思:\n"
        for message in event['reflect']['messages']:
            reflect_md += f"- {message.content}\n"

        with open(reflect_file_path, 'a') as f:  # 使用 'a' 模式追加内容
            f.write(reflect_md + "\n")
        # display(Markdown(reflect_md))


# 异步主函数
async def main():
    # 设置初始输入
    inputs = {
        "messages": [
            HumanMessage(content="给我生成一个关于大模型的文章")
        ],
    }

    config = {"configurable": {"thread_id": "1"}}

    # 构建状态图
    graph = build_graph()
    print(graph.input_schema.schema())
    print(graph.output_schema.schema())
    # 运行状态图
    async for event in graph.astream(inputs, config):
        pretty_print_event_markdown(event)


# 主程序入口
if __name__ == "__main__":
    asyncio.run(main())
