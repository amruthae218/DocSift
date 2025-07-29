# frontend.py
from nicegui import ui
import httpx
import asyncio
from text_extractor import extract_text
from phi_scrubber import scrub_phi

BACKEND_URL = "http://127.0.0.1:8000/process_receipt"

# Shared UI components
def show_header():
    with ui.header().classes('bg-blue-600 text-white'):
        ui.label("DocSift AI").classes('text-xl font-bold')
        ui.link("Home", "/").classes('mx-4')
        ui.link("Login", "/login").classes('mx-4')
        ui.link("Signup", "/signup").classes('mx-4')
        ui.link("Upload", "/upload").classes('mx-4')

def show_footer():
    with ui.footer().classes('bg-gray-200 text-center p-4'):
        ui.label("© 2025 DocSift AI – All rights reserved")

# Pages Definitions

@ui.page('/')
def home():
    show_header()
    with ui.column().classes("p-8 items-center"):
        ui.label("Welcome to DocSift AI!").classes("text-3xl font-bold")
        ui.label("Secure Medical Document Processing with AI").classes("text-lg mt-2 text-gray-700")
    show_footer()

@ui.page('/login')
def login():
    show_header()
    with ui.column().classes("p-8 items-center max-w-md mx-auto"):
        ui.label("Login").classes("text-2xl font-semibold")
        email = ui.input("Email").props('outlined').classes("w-full")
        password = ui.input("Password", password=True).props('outlined').classes("w-full")

        def handle_login():
            if email.value and password.value:
                ui.notify("Logged in successfully!")
                ui.navigate.to('/upload')
            else:
                ui.notify("Please enter valid credentials.", type="warning")

        ui.button("Login", on_click=handle_login).classes("mt-4 w-full")
    show_footer()

@ui.page('/signup')
def signup():
    show_header()
    with ui.column().classes("p-8 items-center max-w-md mx-auto"):
        ui.label("Sign Up").classes("text-2xl font-semibold")
        email = ui.input("Email").props('outlined').classes("w-full")
        password = ui.input("Password", password=True).props('outlined').classes("w-full")
        confirm_password = ui.input("Confirm Password", password=True).props('outlined').classes("w-full")

        def handle_signup():
            if email.value and password.value and confirm_password.value:
                if password.value != confirm_password.value:
                    ui.notify("Passwords do not match.", type="warning")
                else:
                    ui.notify("Signed up successfully!")
                    ui.navigate.to('/upload')
            else:
                ui.notify("Please fill all fields validly.", type="warning")

        ui.button("Sign Up", on_click=handle_signup).classes("mt-4 w-full")
    show_footer()

@ui.page('/upload')
def upload_page():
    show_header()
    with ui.column().classes("p-8 items-center max-w-xl mx-auto w-full"):
        ui.label("Upload Medical Receipt").classes("text-xl font-semibold mb-4")

        uploaded_file_holder = {'file': None}

        def on_file_upload(e):
            e.content.seek(0)
            content_bytes = e.content.read()
            if content_bytes and len(content_bytes) > 0:
                uploaded_file_holder['file'] = {
                    'name': e.name,
                    'content': content_bytes,
                    'type': e.type,
                }

        file_input = ui.upload(
            on_upload=on_file_upload,
            multiple=False,
            label="Upload PDF, Image, or Doc"
        )
        
        result_area = ui.textarea(label='Scrubbed Text').classes('w-full h-48 mt-4')
        result_area.disable()

        cleaned_text_holder = {'value': ''}

        def handle_extract():
            file = uploaded_file_holder['file']
            if not file:
                result_area.value = "Please upload a file first!"
                return

            file_name = file['name']
            file_bytes = file['content']

            # Your existing extract_text and scrub_phi functions
            raw_text = extract_text(file_bytes, file_name)
            cleaned_text = scrub_phi(raw_text)

            cleaned_text_holder['value'] = cleaned_text
            result_area.value = cleaned_text

        def send_to_backend():
            cleaned = cleaned_text_holder['value']
            if not cleaned.strip():
                result_area.value = "Nothing to send. Please extract and scrub first."
                return

            async def send_async():
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            BACKEND_URL,
                            json={"text": cleaned}
                        )
                        if response.status_code == 200:
                            result_area.value = f"✅ Backend responded:\n{response.json()['received']}"
                        else:
                            result_area.value = f"❌ Server error: {response.status_code}"
                except Exception as e:
                    result_area.value = f"❌ Request failed: {e}"

            asyncio.create_task(send_async())

        ui.button("Extract & Scrub", on_click=handle_extract).classes('mr-2')
        ui.button("Submit to Backend", on_click=send_to_backend)
        ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')).classes('mt-4')

    show_footer()




if __name__ == '__main__':
    ui.run(title="DocSift AI", reload=False)
