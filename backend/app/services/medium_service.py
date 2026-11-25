"""
Medium Publishing Service
Handles authentication and article publishing via Medium's REST API.
"""

from typing import List, Optional, Dict, Any
import httpx

MEDIUM_API_BASE = "https://api.medium.com/v1"


class MediumServiceError(Exception):
    """Custom exception for Medium API failures."""
    pass


def get_user_profile(token: str) -> Dict[str, Any]:
    """
    Fetches the authenticated Medium user's profile details.
    GET https://api.medium.com/v1/me
    """
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{MEDIUM_API_BASE}/me", headers=headers)
            if resp.status_code == 401:
                raise MediumServiceError(
                    "Invalid Medium Integration Token. Please check your token in Medium Settings > Security > Integration tokens."
                )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            return data
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        raise MediumServiceError(f"Medium API error ({e.response.status_code}): {error_detail}")
    except httpx.RequestError as e:
        raise MediumServiceError(f"Failed to connect to Medium API: {str(e)}")


def publish_article_to_medium(
    token: str,
    title: str,
    markdown_content: str,
    tags: Optional[List[str]] = None,
    publish_status: str = "draft",
    canonical_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Publishes an article to the user's Medium account.
    POST https://api.medium.com/v1/users/{authorId}/posts

    :param token: Medium Integration Token
    :param title: Article Title
    :param markdown_content: Article content in markdown
    :param tags: Up to 5 tags for categorization
    :param publish_status: 'draft', 'public', or 'unlisted'
    :param canonical_url: Original YouTube or reference URL
    """
    if not token or not token.strip():
        raise MediumServiceError("Medium Integration Token is required.")

    # 1. Fetch Author Profile to get authorId
    user_data = get_user_profile(token)
    author_id = user_data.get("id")
    author_name = user_data.get("name") or user_data.get("username") or "Medium Author"

    if not author_id:
        raise MediumServiceError("Could not retrieve author ID from Medium profile.")

    # Medium allows at most 5 tags, each <= 25 characters
    sanitized_tags = []
    if tags:
        for t in tags[:5]:
            cleaned = t.strip()[:25]
            if cleaned:
                sanitized_tags.append(cleaned)

    # 2. Construct Post Payload
    payload = {
        "title": title[:100],  # Title limit
        "contentFormat": "markdown",
        "content": markdown_content,
        "tags": sanitized_tags,
        "publishStatus": publish_status if publish_status in ["draft", "public", "unlisted"] else "draft",
        "notifyFollowers": publish_status == "public",
    }

    if canonical_url and canonical_url.startswith("http"):
        payload["canonicalUrl"] = canonical_url

    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # 3. Post to Medium
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{MEDIUM_API_BASE}/users/{author_id}/posts",
                headers=headers,
                json=payload,
            )
            if resp.status_code == 400:
                raise MediumServiceError(f"Medium rejected article payload: {resp.text}")
            resp.raise_for_status()
            post_data = resp.json().get("data", {})
            return {
                "success": True,
                "post_id": post_data.get("id"),
                "post_url": post_data.get("url"),
                "publish_status": post_data.get("publishStatus", publish_status),
                "title": post_data.get("title", title),
                "author_name": author_name,
                "author_url": user_data.get("url"),
            }
    except httpx.HTTPStatusError as e:
        raise MediumServiceError(f"Medium post creation failed ({e.response.status_code}): {e.response.text}")
    except httpx.RequestError as e:
        raise MediumServiceError(f"Network error while posting to Medium: {str(e)}")
