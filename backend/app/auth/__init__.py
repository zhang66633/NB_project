"""Auth module — GitHub OAuth login + JWT session management."""

from .schemas import GitHubUser, TokenResponse, UserResponse
from .github import GitHubOAuthClient, get_oauth_client, ALLOWED_CONTRIBUTORS
from .dependencies import (
    create_jwt,
    decode_jwt,
    get_current_user,
    require_auth,
    require_contributor,
)

__all__ = [
    "GitHubUser",
    "TokenResponse",
    "UserResponse",
    "GitHubOAuthClient",
    "get_oauth_client",
    "ALLOWED_CONTRIBUTORS",
    "create_jwt",
    "decode_jwt",
    "get_current_user",
    "require_auth",
    "require_contributor",
]
