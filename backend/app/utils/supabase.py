import os
from supabase import create_client, Client

SUPABASE_URL = "https://zlwixccfktvgyrurvrlp.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")  # Store this securely

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(file_path: str, bucket_name: str, project_id: str, doc_id: str) -> str:
    """
    Uploads a file to Supabase Storage using `project_id-doc_id` as the filename.
    
    :param file_path: Local path of the file to be uploaded.
    :param bucket_name: Supabase storage bucket name.
    :param project_id: Unique identifier of the project.
    :param doc_id: Unique identifier of the document.
    :return: Public URL of the uploaded file.
    """
    try:
        # Set the filename as "projectId-docId"
        supabase_filename = f"projectid-{project_id}-docid-{doc_id}.pdf"

        with open(file_path, "rb") as file:
            response = supabase.storage.from_(bucket_name).upload(supabase_filename, file)

        if hasattr(response, "error") and response.error:
            raise Exception(f"Failed to upload file: {response.error['message']}")

        # Generate public URL
        file_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{supabase_filename}"
        return file_url

    except Exception as e:
        raise Exception(f"Failed to upload file to Supabase: {str(e)}")

def delete_from_supabase(file_url: str, bucket_name: str):
    """
    Deletes a file from Supabase storage.
    
    :param file_url: The full public URL of the file in Supabase to be deleted.
    :param bucket_name: Supabase storage bucket name.
    """
    if not file_url or file_url == "default":
        print("Skipping deletion: No valid file URL provided.")
        return

    try:
        # Extract file path from the public URL
        file_path = file_url.split(f"/storage/v1/object/public/{bucket_name}/")[-1]

        # Perform delete operation
        response = supabase.storage.from_(bucket_name).remove([file_path])

        if hasattr(response, "error") and response.error:
            raise Exception(f"Failed to delete file: {response.error['message']}")

        print(f"Deleted file from Supabase: {file_url}")

    except Exception as e:
        print(f"Error deleting file from Supabase: {str(e)}")


