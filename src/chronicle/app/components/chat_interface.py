"""Chat interface component for Streamlit."""

from __future__ import annotations

import streamlit as st
from chronicle.app.components.story_card import render_story_card


def render_chat_interface(engine) -> None:
    """Render the conversational chatbot interface."""
    st.markdown(
        '<div style="margin-bottom: 1.5rem;">'
        '<h2 style="font-family: \'Cinzel\', \'Palatino Linotype\', Georgia, serif; '
        'color: #E8E2D8; margin-bottom: 0.25rem;">Oracle Dialogue & Narrative Query</h2>'
        '<p style="color: #9BA3AF; font-size: 0.95rem; font-family: Georgia, serif;">'
        'Inquire into classical Greek mythology: retrieve canonical retellings, trace character genealogies, or explore thematic motifs.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    # Initialize chat message history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Greetings, seeker of ancient lore. I am your guide through the classical Greek canon. "
                    "Inquire about any deity or mortal, request full myth narrations, trace ancestral relationships, "
                    "or explore overarching themes such as hubris, fate, and wisdom."
                ),
                "story_card": None,
            }
        ]

    # Quick prompt suggestions (2x2 layout, no three in a row, no emojis)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        if st.button("Myth: Prometheus & The Gift of Fire", use_container_width=True):
            st.session_state.next_input = "Summarize the myth of Prometheus"
        if st.button("Genealogy: Zeus & Hera Relationship", use_container_width=True):
            st.session_state.next_input = "What is the relationship between Zeus and Hera?"
    with p_col2:
        if st.button("Figure: Background of Athena", use_container_width=True):
            st.session_state.next_input = "Tell me about Athena"
        if st.button("Comparison: Athena vs Ares Warfare Philosophy", use_container_width=True):
            st.session_state.next_input = "Compare Athena and Ares"

    st.markdown('<hr style="border: none; border-top: 1px solid #2B2F36; margin: 16px 0;">', unsafe_allow_html=True)

    # Display past conversation turns
    for message in st.session_state.messages:
        role = message["role"]
        with st.chat_message(role):
            st.markdown(message["content"])
            if message.get("story_card"):
                render_story_card(message["story_card"])

    # Chat input
    user_input = st.chat_input("Inquire about any myth, deity, or lineage...")
    if not user_input and "next_input" in st.session_state:
        user_input = st.session_state.pop("next_input")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Consulting the classical archives..."):
            result = engine.chat(user_input)
            response_text = result.get("response", "")
            myth = result.get("myth")

        with st.chat_message("assistant"):
            st.markdown(response_text)
            if myth:
                render_story_card(myth)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response_text,
                "story_card": myth,
            }
        )
