import os
from openai import OpenAI
from dotenv import load_dotenv
from rich import print
import streamlit as st

# Set Streamlit app title
st.title("Chat: Text & Image Generator")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    print("[red]OPENAI_API_KEY not found. Please check your .env file.[/red]")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Set default model and message history in session
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept new user input
if prompt := st.chat_input("Ask something or describe an image you want..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Keywords to trigger image generation
    image_keywords = ["generate an image", "draw", "create an image", "image of", "picture of", "visualize"]

    # If prompt is asking for an image, use DALL·E
    if any(keyword in prompt.lower() for keyword in image_keywords):
        with st.chat_message("assistant"):
            st.markdown("🧠 Generating image...")

            try:
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )

                image_url = image_response.data[0].url

                st.image(image_url, caption="🖼️ Here's your image!")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Here is your image:\n\n![Generated Image]({image_url})"
                })
            except Exception as e:
                st.error(f"Failed to generate image: {e}")
    else:
        # Otherwise, use GPT-4o to respond with text
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})
