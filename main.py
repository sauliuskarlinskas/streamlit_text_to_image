import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from rich import print  # Useful for CLI, not Streamlit, but kept for debugging

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    st.error("❌ OPENAI_API_KEY not found. Please check your .env file.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Streamlit App Title
st.title("💬 Chat: Text & Image Generator")

# Initialize session state for model and messages
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Image upload widget
uploaded_image = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

# Handle image upload
if uploaded_image:
    # Display image in UI
    st.image(uploaded_image, caption="📸 Uploaded Image", use_column_width=True)

    # Encode image to base64
    image_bytes = uploaded_image.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    image_data_url = f"data:image/jpeg;base64,{base64_image}"

    # Append image message for GPT-4o to use
    image_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Here's an image I uploaded."},
            {"type": "image_url", "image_url": {"url": image_data_url}}
        ]
    }
    st.session_state.messages.append(image_message)

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        else:
            for block in message["content"]:
                if block["type"] == "text":
                    st.markdown(block["text"])
                elif block["type"] == "image_url":
                    st.image(block["image_url"]["url"], use_column_width=True)

# User prompt input
if prompt := st.chat_input("Ask something or describe an image you want..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for image generation keywords
    image_keywords = ["generate an image", "draw", "create an image", "image of", "picture of", "visualize"]
    is_image_request = any(keyword in prompt.lower() for keyword in image_keywords)

    with st.chat_message("assistant"):
        if is_image_request:
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
            # GPT-4o handles normal chat prompts
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=st.session_state.messages,
                    stream=True,
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Failed to get response: {e}")
