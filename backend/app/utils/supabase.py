import os
from supabase import create_client, Client

SUPABASE_URL = "https://zlwixccfktvgyrurvrlp.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")  # Store this securely

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(file_path: str, bucket_name: str, file_name: str) -> str:
    """
    Uploads a file to Supabase Storage and returns the public file URL.
    """
    try:
        with open(file_path, "rb") as file:
            response = supabase.storage.from_(bucket_name).upload(file_name, file)

        if hasattr(response, "error") and response.error:
            raise Exception(f"Failed to upload file: {response.error['message']}")

        # Generate public URL
        file_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
        return file_url

    except Exception as e:
        raise Exception(f"Failed to upload file to Supabase: {str(e)}")

