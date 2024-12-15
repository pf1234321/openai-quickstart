import warnings

import pymysql
from dotenv import load_dotenv, find_dotenv
from langchain import hub
from langchain.schema.output_parser import StrOutputParser
from langchain_community.chat_models import ChatOpenAI
import json
import requests
# 忽略DeprecationWarning警告
warnings.filterwarnings("ignore")
_ = load_dotenv(find_dotenv())

# 使用 pymysql 连接数据库
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='zbzx'
)
print("Database connection established")


# 手动获取表信息
def get_table_info(x):
    table_info = []
    try:
        with connection.cursor() as cursor:
            # 查询所有表名
            cursor.execute('SHOW TABLES')
            table_names = cursor.fetchall()
            print(f"Table names: {table_names}")
            for (table_name,) in table_names:
                # 查询每个表的列信息
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = cursor.fetchall()
                column_names = [col[0] for col in columns]
                table_info.append(f"Table: {table_name}, Columns: {column_names}")
        return "\n".join(table_info)
    except Exception as e:
        print(f"Error getting table info: {e}")
        return ""


# 拉取text-to-sql提示模板
prompt = hub.pull("rlm/text-to-sql")
print(f"prompt=={prompt}")

# 初始化语言模型（根据实际情况配置，如设置温度等参数）
model = ChatOpenAI()
print("Model initialized")


# 定义输入处理函数，用于获取相关信息
def get_question(x):
    return x["question"]


def get_few_shot_examples(x):
    # 提供一个示例，用于指导模型生成正确的SQL查询
    return ("Question: 北京大学有多少个学科?\nSQLQuery: SELECT subject_count FROM school_info WHERE school_name = '北京大学'"
            "\nSQLResult: [假设查询结果为学科数量]\nAnswer: 假设查询结果为学科数量")


def get_dialect(x):
    return "mysql"


# 创建输入字典，包含获取各种信息的函数
inputs = {
    "table_info": get_table_info,
    "input": get_question,
    "few_shot_examples": get_few_shot_examples,
    "dialect": get_dialect
}

# 使用LangChain表达式语言创建处理链
sql_response = (
        inputs
        | prompt
        | model.bind(stop=["\nSQLResult:"])
        | StrOutputParser()
)

# 调用处理链，传入问题并获取SQL响应
try:
    # result = sql_response.invoke({"question": "根据产品类型债券产品E查询头寸明细"})
    # result = sql_response.invoke({"question": "查询产品类型不是债券产品E汇总计算头寸金额"})
    result = sql_response.invoke({"question": "统计产品名称不是‘证券产品H’的头寸金额"})
    # 请替换为你的实际API endpoint
    # API_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    # # 替换为你自己的API密钥
    # API_KEY = "87f313a40cf8363057b8bf1c33b85a45.Z2hWx17LfQYiF5eY"
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': f'Bearer {API_KEY}'
    # }
    # data = {
    #     "model": "glm-4",  # 可根据实际可用模型调整
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": "你好"
    #         }
    #     ]
    # }
    # response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
    # result = sql_response.invoke({"question": "根据产品类型是债券产品E汇总计算头寸金额"})
    # result = sql_response.invoke({"question": "模糊查询第六十八中学学科明细?"})
    # result = sql_response.invoke({"question": "长春市第六十八中学科明细?"})
    # result = sql_response.invoke({"question": "长春市第六十八中学一共有多少个学科?"})
    print(f"Result: {result}")
except Exception as e:
    print(f"Error invoking sql_response: {e}")

# 执行生成的SQL查询
try:
    if result:
        query = result.strip().split("SQLQuery: ")[1].strip()
        print(f"Executing SQL query: {query}")
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            for row in result:
                print(row)
    else:
        print("No SQL query generated.")
except Exception as e:
    print(f"Error executing SQL query: {e}")

# 关闭数据库连接
connection.close()
print("Database connection closed")
