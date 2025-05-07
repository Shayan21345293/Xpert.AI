import streamlit as st
from google import genai
import asyncio

# Replace with your actual Gemini API key using Streamlit secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash-live-001"
st.title("Xpert.AI")
# Initialize Gemini client (only if API key is available)
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    st.error("Gemini API key not found. Please add it to Streamlit secrets.")

# Helper function to send and receive messages from Gemini
async def generate_response(user_message):
    full_response = ""
    if client:
        try:
            async with client.aio.live.connect(
                model=MODEL_NAME, config={"response_modalities": ["TEXT"]}
            ) as model:
                await model.send_client_content(
                    turns={"role": "user", "parts": [{"text": user_message}]}, turn_complete=True
                )
                async for response in model.receive():
                    if response.text is not None:
                        full_response += response.text
                        yield full_response
        except Exception as e:
            st.error(f"An error occurred: {e}")
            yield "Sorry, something went wrong. Please try again later."
    else:
        yield "API key not available."

# Helper function to run async code
def run_async_code():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

# The main function to control the chat flow
async def main():
    st.title("Gemini Live Chatbot")

    # Ensure messages are stored in session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

    # Display previous chat history
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input (chat message)
    if prompt := st.chat_input("Type your message here..."):
        # Append the user's message to the chat history
        st.session_state["messages"].append({"role": "user", "content": prompt})
        
        # Display the user's message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Wait for the assistant's response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()  # Placeholder for assistant's message
            full_response = ""
            async for chunk in generate_response(prompt):
                full_response = chunk
                message_placeholder.markdown(full_response + "▌")  # Display typing indicator
            message_placeholder.markdown(full_response)  # Final response

        # Append assistant's message to chat history
        st.session_state["messages"].append({"role": "assistant", "content": full_response})

    # Auto-scroll: Display a placeholder and force the page to scroll to the bottom
    if st.session_state["messages"]:
        with st.empty():
            pass

# Run the async code
if __name__ == "__main__":
    run_async_code()
