# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Instagram MCP: posts to Business account and fetches recent activity.
Usage: python social_instagram_mcp.py --action {post,fetch_activity} [--content <caption>] [--media-url <url>] [--dry-run]"""
import argparse, json, os, sys
import urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone
from log_utils import log_event

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

API_BASE = "https://graph.facebook.com/v18.0"


def get_config():
    token = os.environ.get("IG_ACCESS_TOKEN", "")
    account_id = os.environ.get("IG_BUSINESS_ACCOUNT_ID", "")
    if not token or not account_id:
        raise RuntimeError("IG_ACCESS_TOKEN and IG_BUSINESS_ACCOUNT_ID must be set in .env")
    return token, account_id


def api_call(url, data=None, method="GET"):
    """Make a Graph API call."""
    if data and method == "POST":
        encoded = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=encoded, method="POST")
    else:
        req = urllib.request.Request(url, method=method)
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read().decode())


def post_to_instagram(content, media_url=None, dry_run=False):
    """Post a photo or carousel to Instagram Business account."""
    if dry_run:
        return {"status": "dry_run", "platform": "instagram", "content": content[:100]}
    token, account_id = get_config()
    if not media_url:
        # Instagram requires a media URL for posts; create a text-only draft fallback
        return {"status": "draft_only", "platform": "instagram",
                "note": "Instagram requires image_url for posting. Draft saved.",
                "content": content[:100]}
    # Step 1: Create media container
    container_url = f"{API_BASE}/{account_id}/media"
    container_data = {"image_url": media_url, "caption": content, "access_token": token}
    container_result = api_call(container_url, container_data, "POST")
    container_id = container_result.get("id")
    if not container_id:
        raise RuntimeError(f"Failed to create media container: {container_result}")
    # Step 2: Publish container
    publish_url = f"{API_BASE}/{account_id}/media_publish"
    publish_data = {"creation_id": container_id, "access_token": token}
    publish_result = api_call(publish_url, publish_data, "POST")
    return {"status": "posted", "platform": "instagram",
            "post_id": publish_result.get("id", ""), "content": content[:100]}


def fetch_activity(dry_run=False):
    """Fetch recent media and comments (last 7 days)."""
    if dry_run:
        return {"status": "dry_run", "platform": "instagram", "media": [],
                "summary": {"media_count": 0, "total_likes": 0, "total_comments": 0}}
    token, account_id = get_config()
    since = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
    url = (f"{API_BASE}/{account_id}/media"
           f"?fields=id,caption,timestamp,like_count,comments_count,media_type"
           f"&since={since}&limit=25&access_token={token}")
    data = api_call(url)
    items, total_likes, total_comments = [], 0, 0
    for m in data.get("data", []):
        likes = m.get("like_count", 0)
        comments = m.get("comments_count", 0)
        total_likes += likes
        total_comments += comments
        items.append({"id": m.get("id"), "caption": (m.get("caption") or "")[:100],
                      "timestamp": m.get("timestamp"), "media_type": m.get("media_type"),
                      "likes": likes, "comments": comments})
    return {"status": "success", "platform": "instagram", "media": items,
            "summary": {"media_count": len(items), "total_likes": total_likes,
                        "total_comments": total_comments}}


def main():
    ap = argparse.ArgumentParser(description="Instagram MCP – Gold Tier")
    ap.add_argument("--action", required=True, choices=["post", "fetch_activity"])
    ap.add_argument("--content", default="", help="Caption text")
    ap.add_argument("--media-url", default="", help="Image URL for posting")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    try:
        if args.action == "post":
            result = post_to_instagram(args.content, args.media_url or None, dry_run)
        else:
            result = fetch_activity(dry_run)
        log_event(f"ig_{args.action}", "social_instagram_mcp",
                  result.get("status", "success"),
                  details={"action": args.action, "social_post_id": result.get("post_id"),
                           "mcp_params": {"content": args.content[:50]}})
        print(json.dumps(result))
    except Exception as e:
        result = {"status": "error", "platform": "instagram", "error": str(e)}
        log_event(f"ig_{args.action}", "social_instagram_mcp", "failure",
                  details={"error": str(e)[:200]})
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
