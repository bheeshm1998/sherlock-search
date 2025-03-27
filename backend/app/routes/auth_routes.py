import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Security, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
import datetime
from supabase import create_client, Client
from fastapi import Query

load_dotenv()
# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

# Auth Request Model
class AuthRequest(BaseModel):
    email: str
    userType: str

# Token Response Model
class TokenResponse(BaseModel):
    token: str

class GroupsResponse(BaseModel):
    groups: List[str]
    total_groups: int
    page: int
    page_size: int


# Login Endpoint
@router.post("/auth/login", response_model=TokenResponse)
async def login(auth_request: AuthRequest):
    # Query Supabase to check if user exists
    response = supabase.table("employees").select("*").eq("email", auth_request.email).execute()

    # Check if user was found
    if not response.data:
        raise HTTPException(status_code=401, detail="Invalid email")

    # Get the first (and should be only) user
    user = response.data[0]

    # Generate JWT Token
    token_data = {
        "email": user["email"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    if(auth_request.userType == "admin"):
        if (user["email"] == "abhishek.a@payoda.com"):
            return {"token": token}
        else :
            raise HTTPException(status_code=401, detail="Not an admin")
    else :
        return {"token": token}


# Dependency to Get Current User from Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Verify user exists in Supabase
        response = supabase.table("employees").select("*").eq("email", payload["email"]).execute()

        # Check if user was found
        if not response.data:
            raise HTTPException(status_code=401, detail="User not found")

        return response.data[0]

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Check if User Belongs to a Group
@router.get("/auth/check-group")
async def check_group(groups: List[str] = Form(...), user: dict = Depends(get_current_user)):
    """
    Check if the user belongs to any of the specified groups.

    :param groups: List of group names to check
    :param user: Current authenticated user
    :return: Message if user belongs to any of the specified groups
    """
    try:
        # First, get the email ID from the email table
        email_response = supabase.table("emails").select("*").eq("email", user["email"]).execute()

        if not email_response.data:
            raise HTTPException(status_code=404, detail="Email not found in system")

        email_id = email_response.data[0]["id"]

        # Fetch user's group memberships
        group_membership_response = (
            supabase.table("email_groups")
            .select("groups(name)")  # Join with groups table to get group names
            .eq("email_id", email_id)
            .execute()
        )

        # Extract user's group names
        user_groups = [
            membership["groups"]["name"]
            for membership in group_membership_response.data
        ]

        # Check if user belongs to any of the requested groups
        matching_groups = set(groups) & set(user_groups)

        if matching_groups:
            return {
                "message": f"{user['email']} belongs to group(s): {', '.join(matching_groups)}",
                "belonging_groups": list(matching_groups)
            }

        raise HTTPException(
            status_code=403,
            detail=f"{user['email']} does not belong to any of the requested groups: {groups}"
        )

    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Error checking group membership: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking group membership")


@router.get("/auth/groups", response_model=Dict[str, Any])
async def list_available_groups(
        user: dict = Depends(get_current_user),
        # Optional pagination parameters
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=100)
):
    """
    Retrieve a list of available groups.

    :param user: Currently authenticated user (ensures only authenticated users can access)
    :param page: Page number for pagination (default: 1)
    :param page_size: Number of groups per page (default: 50, max: 100)
    :return: List of group names
    """
    try:
        # Calculate offset for pagination
        offset = (page - 1) * page_size

        # Fetch groups with pagination
        groups_response = (
            supabase.table("groups")
            .select("name")
            .range(offset, offset + page_size - 1)
            .execute()
        )

        # Extract group names
        groups = [group['name'] for group in groups_response.data or []]

        # Optional: Get total count of groups for metadata
        count_response = supabase.table("groups").select("name", count="exact").execute()
        total_groups = count_response.count if count_response.count is not None else 0

        # Return groups with optional metadata
        return {
            "groups": groups,
            "total_groups": total_groups
        }

    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Error retrieving groups: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving available groups")


# Optional: Pydantic model for structured response
