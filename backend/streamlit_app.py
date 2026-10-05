import os
from typing import Any, Optional

import httpx
import streamlit as st

DEFAULT_BACKEND_URL = os.getenv("CAMPUSAI_BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="CampusAI", page_icon="🎓", layout="wide")


def api_url(path: str) -> str:
    base = st.session_state.get("backend_url", DEFAULT_BACKEND_URL).rstrip("/")
    return f"{base}{path}"


def api_request(
    method: str,
    path: str,
    *,
    token: Optional[str] = None,
    json_data: Optional[dict[str, Any]] = None,
    files: Optional[dict[str, Any]] = None,
    data: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if json_data is not None and files is None:
        headers["Content-Type"] = "application/json"

    response = httpx.request(
        method=method,
        url=api_url(path),
        headers=headers,
        json=json_data,
        files=files,
        data=data,
        timeout=60,
    )

    try:
        payload = response.json()
    except ValueError:
        payload = {"detail": response.text}

    if response.is_error:
        message = payload.get("detail", payload)
        raise RuntimeError(f"{response.status_code}: {message}")

    return payload


def login_user(email: str, password: str) -> str:
    data = {"username": email, "password": password}
    response = api_request("POST", "/api/auth/login", data=data)
    token = response.get("access_token")
    if not token:
        raise RuntimeError("No access token was returned by the backend.")
    return token


def load_documents(token: str) -> list[dict[str, Any]]:
    return api_request("GET", "/api/documents/", token=token)


def upload_document(token: str, uploaded_file) -> dict[str, Any]:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
    return api_request("POST", "/api/documents/upload", token=token, files=files)


if "backend_url" not in st.session_state:
    st.session_state.backend_url = DEFAULT_BACKEND_URL
if "token" not in st.session_state:
    st.session_state.token = None
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None


with st.sidebar:
    st.title("CampusAI")
    st.text_input("Backend URL", key="backend_url")

    if st.session_state.token:
        st.success("Authenticated")
        if st.button("Log out"):
            st.session_state.token = None
            st.session_state.conversation_id = None
            st.rerun()
    else:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                try:
                    st.session_state.token = login_user(email, password)
                    st.success("Logged in successfully.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Login failed: {exc}")

        st.caption("Tip: create a user in the backend app first if this is a fresh database.")

    st.divider()
    if st.button("Check backend health"):
        try:
            health = api_request("GET", "/api/health")
            st.json(health)
        except Exception as exc:
            st.error(f"Backend unreachable: {exc}")


st.title("🎓 CampusAI Assistant")

if not st.session_state.token:
    st.info("Log in from the sidebar to start chatting or uploading academic documents.")
    st.stop()


with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("AI Chat")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Ask a question about your course or documents")
        if prompt:
            user_message = {"role": "user", "content": prompt}
            st.session_state.messages.append(user_message)
            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                payload = {
                    "message": prompt,
                    "mode": "academic_rag",
                    "conversation_id": st.session_state.conversation_id,
                }
                response = api_request("POST", "/api/chat/", token=st.session_state.token, json_data=payload)
                st.session_state.conversation_id = response.get("conversation_id")
                bot_reply = response.get("response", "No response returned.")
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)

                if response.get("sources"):
                    with st.expander("Sources"):
                        for source in response["sources"]:
                            st.write(source)
            except Exception as exc:
                st.error(f"Chat request failed: {exc}")

    with col2:
        st.subheader("Documents")
        uploaded_files = st.file_uploader(
            "Upload course materials",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    document = upload_document(st.session_state.token, uploaded_file)
                    st.success(f"Uploaded: {document.get('file_name', uploaded_file.name)}")
                except Exception as exc:
                    st.error(f"Upload failed for {uploaded_file.name}: {exc}")

        try:
            documents = load_documents(st.session_state.token)
            if documents:
                for document in documents:
                    st.write(f"- {document.get('file_name', 'Untitled document')}")
            else:
                st.caption("No uploaded documents yet.")
        except Exception as exc:
            st.error(f"Could not load documents: {exc}")

        st.divider()
        st.subheader("Quick actions")
        st.markdown(
            """
            - Ask questions based on uploaded material.
            - Switch between academic RAG and basic LLM mode if your backend supports it.
            - Keep the backend URL pointed at the running FastAPI server.
            """
        )
