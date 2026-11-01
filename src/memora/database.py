import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def sign_in_with_pass(client: Client):
    email = os.getenv("USER_EMAIL")
    password = os.getenv("USER_PASS")

    if not email or not password:
        raise ValueError("USER_EMAIL and USER_PASS must be set in .env")

    return client.auth.sign_in_with_password(
        {"email": email, "password": password}
    )


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    client = create_client(url, key)
    sign_in_with_pass(client)
    return client