"""Streamlit front end for the existing Sales & Inventory Genie Agent."""

import os
from collections.abc import Mapping
from typing import Any

import streamlit as st
from databricks.sdk import WorkspaceClient


APP_TITLE = "Sales & Inventory Assistant"
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", "").strip()
QUICK_PROMPTS = (
    "Revenue overview",
    "Low stock",
    "Inventory by warehouse",
    "Top product categories",
)


def _value(source: Any, *keys: str) -> Any:
    """Read the first available key or attribute without assuming an SDK shape."""
    if source is None:
        return None

    for key in keys:
        if isinstance(source, Mapping):
            value = source.get(key)
        else:
            value = getattr(source, key, None)
        if value is not None:
            return value
    return None


def _enum_name(value: Any) -> str:
    raw_value = _value(value, "value")
    return str(raw_value if raw_value is not None else value or "").upper()


def _message_payload(response: Any) -> Any:
    """Support direct GenieMessage responses and older nested message responses."""
    if _value(response, "attachments") is not None:
        return response
    return _value(response, "message") or response


def parse_genie_response(response: Any) -> tuple[str, list[str]]:
    """Extract user-facing text and generated SQL; never expose Genie thoughts."""
    message = _message_payload(response)
    final_texts: list[str] = []
    fallback_texts: list[str] = []
    sql_queries: list[str] = []

    attachments = _value(message, "attachments") or []
    for attachment in attachments:
        text_attachment = _value(attachment, "text")
        if isinstance(text_attachment, str):
            text_content = text_attachment.strip()
            purpose = ""
        else:
            text_content = str(
                _value(text_attachment, "content", "text") or ""
            ).strip()
            purpose = _enum_name(_value(text_attachment, "purpose"))

        if text_content:
            fallback_texts.append(text_content)
            if "ANSWER" in purpose:
                final_texts.append(text_content)

        query_attachment = _value(attachment, "query")
        if isinstance(query_attachment, str):
            sql = query_attachment.strip()
        else:
            sql = str(
                _value(query_attachment, "query", "sql", "statement") or ""
            ).strip()

        if sql and sql not in sql_queries:
            sql_queries.append(sql)

    answer = "\n\n".join(final_texts or fallback_texts)
    return answer, sql_queries


@st.cache_resource
def workspace_client() -> WorkspaceClient:
    """Use Databricks Apps managed authentication; no token is supplied in code."""
    return WorkspaceClient()


def ask_genie(question: str) -> tuple[str, list[str]]:
    client = workspace_client()
    conversation_id = st.session_state.conversation_id

    if conversation_id:
        response = client.genie.create_message_and_wait(
            space_id=GENIE_SPACE_ID,
            conversation_id=conversation_id,
            content=question,
        )
    else:
        response = client.genie.start_conversation_and_wait(
            space_id=GENIE_SPACE_ID,
            content=question,
        )
        payload = _message_payload(response)
        conversation_id = _value(response, "conversation_id") or _value(
            payload, "conversation_id"
        )
        if not conversation_id:
            raise RuntimeError("Genie did not return a conversation ID.")
        st.session_state.conversation_id = str(conversation_id)

    return parse_genie_response(response)


def render_message(message: dict[str, Any]) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        sql_queries = message.get("sql") or []
        if sql_queries:
            with st.expander("Generated SQL"):
                st.code("\n\n-- Next generated query\n\n".join(sql_queries), language="sql")


st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

st.title(APP_TITLE)
st.caption("Ask the governed Sales & Inventory Analytics Agent in plain language.")

if st.sidebar.button("Start a new conversation", use_container_width=True):
    st.session_state.messages = []
    st.session_state.conversation_id = None
    st.rerun()

if not GENIE_SPACE_ID:
    st.error(
        "GENIE_SPACE_ID is not configured. Add the existing Genie Agent as an "
        "App Resource with key `genie-space`, grant it **Can run**, and redeploy."
    )
    st.stop()

st.markdown("**Try a quick prompt**")
quick_prompt = None
columns = st.columns(2)
for index, label in enumerate(QUICK_PROMPTS):
    with columns[index % 2]:
        if st.button(label, key=f"quick_prompt_{index}", use_container_width=True):
            quick_prompt = label

for stored_message in st.session_state.messages:
    render_message(stored_message)

typed_prompt = st.chat_input("Ask a question about sales or inventory...")
prompt = quick_prompt or typed_prompt

if prompt:
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    render_message(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Asking the Sales & Inventory Analytics Agent..."):
            try:
                answer, sql_queries = ask_genie(prompt)
            except Exception as error:  # Streamlit must keep the session usable.
                st.error(
                    "I couldn't get an answer from Genie. Verify the App Resource, "
                    "the agent permission, and the app service principal's Gold data "
                    "permissions, then try again."
                )
                st.caption(f"Error type: {type(error).__name__}")
            else:
                if not answer:
                    answer = (
                        "Genie completed the request but did not return a final text "
                        "response."
                    )
                assistant_message = {
                    "role": "assistant",
                    "content": answer,
                    "sql": sql_queries,
                }
                st.session_state.messages.append(assistant_message)
                st.markdown(answer)
                if sql_queries:
                    with st.expander("Generated SQL"):
                        st.code(
                            "\n\n-- Next generated query\n\n".join(sql_queries),
                            language="sql",
                        )
