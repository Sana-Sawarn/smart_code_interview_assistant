import streamlit as st
from llm import get_response, explain_code_result, get_rag_response
from code_runner import run_python_code
from rag import retrieve_context, create_vector_store
from voice import speak_text, stop_speaking

st.set_page_config(page_title="Smart Code Interview Assistant", layout="wide")
st.title("💻 Smart Code Interview Assistant")
output_mode = st.radio(
    "Select Output Mode:",
    ["Text Only", "Audio Only", "Text + Audio"]
)
# -----------------------------
# Session state setup
# -----------------------------
if "last_mode" not in st.session_state:
    st.session_state.last_mode = "Normal Answer"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_code" not in st.session_state:
    st.session_state.last_code = ""

if "last_output" not in st.session_state:
    st.session_state.last_output = ""

# -----------------------------
# Mode selection
# -----------------------------
mode = st.radio("Select Mode:", ["Normal Answer", "Hint Mode"])

# Reset chat if mode changes
if mode != st.session_state.last_mode:
    st.session_state.messages = []
    st.session_state.last_mode = mode

# -----------------------------
# Chat section
# -----------------------------
st.subheader("🤖 Interview Assistant")

user_input = st.text_input("Ask or continue your answer:")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    send_clicked = st.button("Send")

with col2:
    clear_clicked = st.button("Clear Chat")

with col3:
    if st.button("🛑 Stop Audio"):
        stop_speaking()

if clear_clicked:
    st.session_state.messages = []
    st.rerun()

if send_clicked:
    if user_input.strip():
        if len(st.session_state.messages) == 0:
            if mode == "Hint Mode":
                system_prompt = (
                    "You are a strict coding interviewer.\n"
                    "Rules:\n"
                    "1. NEVER explain the full problem.\n"
                    "2. NEVER give the full solution.\n"
                    "3. Give ONLY one hint at a time.\n"
                    "4. Ask ONLY one short question.\n"
                    "5. DO NOT praise the user.\n"
                    "6. DO NOT say 'correct' or 'good'.\n"
                    "7. Keep the answer under 2 lines.\n"
                    "8. If the user is stuck, give the next small hint.\n"
                    "9. Be direct and minimal.\n"
                )
            else:
                system_prompt = (
                    "You are a coding interview assistant.\n"
                    "Rules:\n"
                    "1. If user asks first time, give a clear structured answer.\n"
                    "2. If user says 'next step', continue from the previous step.\n"
                    "3. Do not repeat the full answer again.\n"
                    "4. Continue logically step by step.\n"
                    "5. Keep answers clear and easy to understand.\n"
                    "6. Avoid repetition.\n"
                )

            st.session_state.messages.append(
                {"role": "system", "content": system_prompt}
            )

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        try:
            with st.spinner("Thinking..."):
                reply = get_response(st.session_state.messages)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            # 🔊 Voice output
            if output_mode == "Audio Only":
                speak_text(reply)

            elif output_mode == "Text + Audio":
                speak_text(reply)

        except Exception as e:
            st.error(f"Unexpected error: {e}")
    else:
        st.warning("Please enter a question.")

# Display chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.write(f"**User:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.write(f"**Assistant:** {msg['content']}")

# -----------------------------
# Code execution section
# -----------------------------
st.subheader("💻 Python Code Execution")

code = st.text_area(
    "Write your Python code here:",
    height=250,
    placeholder='print("Hello World")'
)

col3, col4 = st.columns([1, 1])

with col3:
    run_clicked = st.button("Run Code")

with col4:
    explain_clicked = st.button("Explain Output/Error")

if run_clicked:
    if code.strip():
        with st.spinner("Running code..."):
            output = run_python_code(code)

        st.session_state.last_code = code
        st.session_state.last_output = output

        st.success("Output:")
        st.code(output, language="text")
    else:
        st.warning("Please enter code before running.")

if st.session_state.last_output:
    st.info("Last execution result:")
    st.code(st.session_state.last_output, language="text")

if explain_clicked:
    if st.session_state.last_code and st.session_state.last_output:
        try:
            with st.spinner("Explaining result..."):
                explanation = explain_code_result(
                    st.session_state.last_code,
                    st.session_state.last_output
                )
            st.subheader("🧠 AI Explanation")
            st.write(explanation)
        except Exception as e:
            st.error(f"Unexpected error while explaining: {e}")
    else:
        st.warning("Run some code first, then I can explain the output or error.")

# -----------------------------
# RAG section
# -----------------------------
st.subheader("📚 Ask Questions From Your DSA PDF Notes")

col5, col6 = st.columns([1, 1])

with col5:
    build_rag_clicked = st.button("Build / Refresh Notes Index")

if build_rag_clicked:
    with st.spinner("Reading PDFs and building vector index..."):
        vectorstore = create_vector_store()

    if vectorstore is not None:
        st.success("Notes index created successfully.")
    else:
        st.warning("No PDF files found inside data/docs.")

rag_question = st.text_input("Ask a question from your uploaded notes:")

if st.button("Ask Notes"):
    if rag_question.strip():
        with st.spinner("Searching notes..."):
            context = retrieve_context(rag_question)
            answer = get_rag_response(rag_question, context)

        st.success("Answer from Notes:")
        st.write(answer)

        with st.expander("📄 Source from Notes"):
            st.write(context)

        # 🔊 Speak RAG answer
        if output_mode == "Audio Only":
            speak_text(answer)

        elif output_mode == "Text + Audio":
            speak_text(answer)

    else:
        st.warning("Please enter a question.")