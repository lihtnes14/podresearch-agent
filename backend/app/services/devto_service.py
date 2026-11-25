"""
Dev.to Publishing Service
Publishes articles directly to Dev.to via their official REST API.
API Reference: https://developers.forem.com/api/v1#tag/articles/operation/createArticle
"""

from typing import List, Optional, Dict, Any
import httpx

DEVTO_API_BASE = "https://dev.to/api"


class DevtoServiceError(Exception):
    """Custom exception for Dev.to API errors."""
    pass


def publish_article_to_devto(
    api_key: str,
    title: str,
    markdown_content: str,
    tags: Optional[List[str]] = None,
    published: bool = False,
    canonical_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Publishes an article to Dev.to.

    :param api_key: Dev.to API Key (from https://dev.to/settings/extensions)
    :param title: Article Title
    :param markdown_content: Article content formatted in Markdown
    :param tags: Up to 4 tags (alphanumeric, lowercase)
    :param published: True to publish immediately, False to save as draft
    :param canonical_url: Original YouTube video URL as canonical link
    :return: Dict containing post_id, post_url, published status, author details
    """
    if not api_key or not api_key.strip():
        raise DevtoServiceError("Dev.to API Key is required.")

    # Clean tags: Dev.to allows up to 4 tags, lowercase alphanumeric, no spaces
    cleaned_tags = []
    if tags:
        for tag in tags[:4]:
            t = "".join(c for c in tag.lower().replace("-", "_").replace(" ", "_") if c.isalnum() or c == "_").strip("_")
            if t and len(t) <= 30 and t not in cleaned_tags:
                cleaned_tags.append(t)

    if not cleaned_tags:
        cleaned_tags = ["podcast", "ai"]

    payload = {
        "article": {
            "title": title[:120],
            "body_markdown": markdown_content,
            "published": published,
            "tags": cleaned_tags,
        }
    }

    if canonical_url and canonical_url.startswith("http"):
        payload["article"]["canonical_url"] = canonical_url

    headers = {
        "api-key": api_key.strip(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{DEVTO_API_BASE}/articles",
                headers=headers,
                json=payload,
            )

            if resp.status_code == 401:
                raise DevtoServiceError(
                    "Invalid Dev.to API Key. Please generate a valid key at https://dev.to/settings/extensions."
                )

            if resp.status_code == 422:
                err_data = resp.json()
                error_msg = err_data.get("error", resp.text)
                raise DevtoServiceError(f"Dev.to rejected the article: {error_msg}")

            resp.raise_for_status()
            data = resp.json()

            return {
                "success": True,
                "post_id": data.get("id"),
                "post_url": data.get("url"),
                "published": data.get("published", published),
                "title": data.get("title", title),
                "author_name": (data.get("user") or {}).get("name") or (data.get("user") or {}).get("username") or "Dev.to Author",
                "author_username": (data.get("user") or {}).get("username"),
            }

    except httpx.HTTPStatusError as e:
        raise DevtoServiceError(f"Dev.to API error ({e.response.status_code}): {e.response.text}")
    except httpx.RequestError as e:
        raise DevtoServiceError(f"Failed to connect to Dev.to API: {str(e)}")
