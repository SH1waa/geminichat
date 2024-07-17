import google.generativeai as genai
import streamlit as st
import time
import random
from utils import SAFETY_SETTTINGS

# 预设提示词，多行字符串使用三引号
preset_prompt = """You are a helpful assistant.
Here are some important rules for the interaction:
1. Be polite and respectful.
2. Provide accurate and relevant information.
3. Ensure clarity and simplicity in explanations."""

st.set_page_config(
    page_title="Chat To XYthing",
    page_icon="🔥",
    menu_items={
        'About': "# Make By hiliuxg"
    }
)

st.title("Chat To XYthing")
st.caption("a chatbot, powered by google gemini pro.")

if "app_key" not in st.session_state:
    app_key = st.text_input("Your Gemini App Key", type='password')
    if app_key:
        st.session_state.app_key = app_key

if "history" not in st.session_state:
    st.session_state.history = [{"role": "system", "content": preset_prompt}]

try:
    genai.configure(api_key=st.session_state.app_key)
except AttributeError as e:
    st.warning("Please Put Your Gemini App Key First.")

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=st.session_state.history)

with st.sidebar:
    if st.button("Clear Chat Window", use_container_width=True, type="primary"):
        st.session_state.history = [{"role": "system", "content": preset_prompt}]  # 重置时保留预设提示词
        st.rerun()

for message in st.session_state.history:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

if "app_key" in st.session_state:
    if prompt := st.chat_input(""):
        user_message = {"role": "user", "content": prompt.replace('\n', '  \n')}
        st.session_state.history.append(user_message)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                full_response = ""
                for chunk in chat.send_message(user_message["content"], stream=True, safety_settings=SAFETY_SETTTINGS):
                    if hasattr(chunk, 'text'):  # 检查 chunk 是否有 text 属性
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "_")
                        time.sleep(0.05)
                message_placeholder.markdown(full_response)
                st.session_state.history.append({"role": "assistant", "content": full_response})
            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.exception(e)
            st.session_state.history = chat.history
