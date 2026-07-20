"""Auth schemas — Pydantic models for authentication."""

from typing import Optional
from pydantic import BaseModel


class GitHubUser(BaseModel):
    """GitHub user profile returned by OAuth."""
    id: int
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT token returned to the frontend after login."""
    access_token: str
    token_type: str = "bearer"
    user: GitHubUser


class UserResponse(BaseModel):
    """Current authenticated user info."""
    authenticated: bool
    user: Optional[GitHubUser] = None
    is_contributor: bool = False
