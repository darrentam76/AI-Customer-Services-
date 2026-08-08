import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import database as db

# 1. 載入 .env 環境變數
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("未找到 API Key，請確保 .env 檔案中有設定 DEEPSEEK_API_KEY")
    st.stop()

# 2. 初始化 Client (連線至 DeepSeek)
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 定義 DeepSeek 指定模型名稱
MODEL_NAME = "deepseek-v4-flash"

st.title("Apex Support Bot 🤖")

# 3. 定義 Function Calling / Tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_details",
            "description": "根據訂單編號查詢訂單詳情",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "訂單編號，例如 1001 或 1002"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "處理訂單退款申請",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "訂單編號"},
                    "reason": {"type": "string", "description": "退款原因"}
                },
                "required": ["order_id", "reason"]
            }
        }
    }
]

# 4. 初始化對話歷史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Apex Support Bot, a helpful customer service assistant. "
                "Guardrails: Refunds strictly capped to items delivered <= 14 days ago. "
                "Never offer > $50 financial compensation without escalation. "
                "Always ask for order ID if missing."
            )
        }
    ]

# 5. 渲染過去的對話歷史
for msg in st.session_state.messages:
    if msg["role"] != "system" and "content" in msg and msg["content"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 6. 處理使用者輸入
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 第一次呼叫 LLM
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=st.session_state.messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    # 檢查是否需要執行 Tool Call
    if response_message.tool_calls:
        st.session_state.messages.append(response_message)
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # 呼叫 database.py 裡面的實體函式
            if function_name == "get_order_details":
                tool_output = db.get_order_details(function_args.get("order_id"))
            elif function_name == "process_refund":
                tool_output = db.process_refund(function_args.get("order_id"), function_args.get("reason"))
            else:
                tool_output = "Unknown function"

            st.session_state.messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(tool_output)
            })

        # 第二次呼叫 LLM (將 Tool 執行結果傳給模型產生對話)
        second_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=st.session_state.messages
        )
        final_text = second_response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": final_text})
        with st.chat_message("assistant"):
            st.markdown(final_text)
    else:
        final_text = response_message.content
        st.session_state.messages.append({"role": "assistant", "content": final_text})
        with st.chat_message("assistant"):
            st.markdown(final_text)
            
            import datetime  # 確保檔案頂部有 import datetime

## 4. 初始化對話歷史（明確指示退款執行邏輯）
if "messages" not in st.session_state:
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                f"Today's date is {today_str}. You are Apex Support Bot, a helpful customer service assistant.\n"
                "Guardrails:\n"
                "- When a user requests a refund and provides an order ID and reason, IMMEDIATELY call the `process_refund` tool.\n"
                "- Do NOT ask the user to confirm dates or manually check return windows yourself—`process_refund` handles all validation.\n"
                "- Never offer > $50 financial compensation without escalation.\n"
                "- Always ask for order ID if missing."
            )
        }
    ]