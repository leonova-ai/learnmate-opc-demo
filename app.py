import os

from gradio_app import CSS, demo


if __name__ == "__main__":
    port = int(os.getenv("PORT") or os.getenv("GRADIO_SERVER_PORT") or "7860")
    server_name = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    demo.launch(server_name=server_name, server_port=port, css=CSS)
