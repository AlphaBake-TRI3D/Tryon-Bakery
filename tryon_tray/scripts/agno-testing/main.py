# demo_chat_image.py
import gradio as gr
from typing import List, Tuple, Dict, Any, Union

def handle_user(
    user_text: str,
    user_image: Any,          # filepath or PIL.Image
    chat_history: List[Tuple[Any, Any]]
) -> Tuple[str, None, List[Tuple[Any, Any]]]:
    """
    • Builds a message combining text + optional image
    • Appends bot reply
    • Clears input fields
    """
    # Build user display payload
    user_msg: Union[Dict[str, Any], str]
    if user_image is not None and user_text.strip():
        user_msg = {"text": user_text.strip(), "image": user_image}
    elif user_image is not None:          # image only
        user_msg = user_image
    else:                                 # text only
        user_msg = user_text.strip()

    chat_history.append(
        (user_msg, "Thanks! We received your message.")
    )
    return "", None, chat_history         # clears textbox & image input


with gr.Blocks(title="Chat + Image Demo") as demo:
    gr.Markdown("### 🧵 FashionAgent – sample chat (echo bot)")

    chatbot = gr.Chatbot(height=450)

    with gr.Row():
        txt_in = gr.Textbox(
            scale=4,
            placeholder="Type a message...",
            show_label=False,
        )
        img_in = gr.Image(
            type="filepath",   # lets Chatbot display it directly
            label=" ",
            scale=2,
        )
        send_btn = gr.Button("Send", variant="primary")

    state = gr.State([])  # stores running chat history list

    # Triggers: button click or pressing Enter in textbox
    send_btn.click(
        handle_user,
        inputs=[txt_in, img_in, state],
        outputs=[txt_in, img_in, chatbot],
    )
    txt_in.submit(
        handle_user,
        inputs=[txt_in, img_in, state],
        outputs=[txt_in, img_in, chatbot],
    )

if __name__ == "__main__":
    demo.launch(share=True)       # add share=True for a public link
