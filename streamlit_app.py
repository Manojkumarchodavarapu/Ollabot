import streamlit as st
import requests
import json
from io import StringIO
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Chatbot", page_icon="👩‍💻", layout="centered")
st.title("Chatbot using Ollama Qwen 2.5 7B")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "saved_conversations" not in st.session_state:
    st.session_state.saved_conversations = []
if "last_response_saved" not in st.session_state:
    st.session_state.last_response_saved = True

# Sidebar: Display saved conversations
st.sidebar.title("🗃️ Saved Chat History")
if st.session_state.saved_conversations:
    combined_text = ""
    for conv in st.session_state.saved_conversations:
        for msg in conv:
            role = msg["role"].capitalize()
            content = msg["content"]
            combined_text += f"{role}: {content}\n\n"

    st.sidebar.text_area("📝 All Saved Conversations", combined_text, height=300)
    
    st.sidebar.download_button(
        label="📥 Download All as .txt",
        data=StringIO(combined_text).getvalue(),
        file_name="all_conversations.txt",
        mime="text/plain"
    )

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.last_response_saved = False
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    def get_context():
        msgs = st.session_state.messages
        return msgs[-6:] if len(msgs) >= 6 else msgs

    with st.chat_message("assistant"):
        placeholder = st.empty()
        asst_msg = ""

        try:
            response = requests.post(
                "http://localhost:11434/v1/chat/completions",
                json={
                    "model": "qwen2.5:7b",
                    "messages": get_context(),
                    "stream": True
                },
                stream=True
            )
        except Exception as exc:
            placeholder.error(f"Request failed: {exc}")
            response = None

        if response:
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="ignore")

                if line.startswith("data:"):
                    line = line[len("data: "):]

                if line.strip() == "DONE":
                    break

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if data.get("choices"):
                    delta = data["choices"][0]["delta"]
                    token = delta.get("content", "")
                    asst_msg += token
                    placeholder.markdown(asst_msg + "▌")

                    if data["choices"][0].get("finish_reason"):
                        break

            placeholder.markdown(asst_msg)
            st.session_state.messages.append({"role": "assistant", "content": asst_msg})

# Save and Copy options after assistant response
if (
    st.session_state.messages 
    and st.session_state.messages[-1]["role"] == "assistant" 
    and not st.session_state.last_response_saved
):
    if st.button("💾 Save this Conversation"):
        if len(st.session_state.messages) >= 2:
            last_pair = st.session_state.messages[-2:]
            if last_pair[0]["role"] == "user" and last_pair[1]["role"] == "assistant":
                st.session_state.saved_conversations.append(last_pair)
        st.session_state.last_response_saved = True
        st.success("Last conversation turn saved!")
        st.rerun()

   
