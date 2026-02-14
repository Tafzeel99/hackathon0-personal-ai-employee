# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Facebook MCP: posts to a Page and fetches recent activity via Graph API.
Usage: python social_facebook_mcp.py --action {post,fetch_activity} [--content <text>] [--dry-run]"""
import argparse, json, os, sys
from datetime import datetime, timedelta, timezone
from log_utils import log_event

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass


def get_config():
    token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
    page_id = os.environ.get("FB_PAGE_ID", "")
    if not token or not page_id:
        raise RuntimeError("FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID must be set in .env")
    return token, page_id


def post_to_page(content, dry_run=False):
    """Post a message to the Facebook Page."""
    if dry_run:
        return {"status": "dry_run", "platform": "facebook", "content": content[:100]}
    try:
        import facebook
        graph = facebook.GraphAPI(access_token=token, version="3.1")
        result = graph.put_object(parent_object=page_id, connection_name="feed",
                                  message=content)
        return {"status": "posted", "platform": "facebook",
                "post_id": result.get("id", ""), "content": content[:100]}
    except ImportError:
        import urllib.request, urllib.parse
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        data = urllib.parse.urlencode({"message": content, "access_token": token}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        return {"status": "posted", "platform": "facebook",
                "post_id": result.get("id", ""), "content": content[:100]}


def fetch_activity(dry_run=False):
    """Fetch recent page posts, likes, and comments (last 7 days)."""
    if dry_run:
        return {"status": "dry_run", "platform": "facebook", "posts": [],
                "summary": {"post_count": 0, "total_likes": 0, "total_comments": 0}}
    token, page_id = get_config()
    since = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
    try:
        import facebook
        graph = facebook.GraphAPI(access_token=token, version="3.1")
        posts = graph.get_connections(page_id, "posts",
                                      fields="message,created_time,likes.summary(true),comments.summary(true)",
                                      since=since, limit=25)
        items = []
        total_likes, total_comments = 0, 0
        for p in posts.get("data", []):
            likes = p.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = p.get("comments", {}).get("summary", {}).get("total_count", 0)
            total_likes += likes
            total_comments += comments
            items.append({"id": p.get("id"), "message": p.get("message", "")[:100],
                          "created": p.get("created_time"), "likes": likes, "comments": comments})
        return {"status": "success", "platform": "facebook", "posts": items,
                "summary": {"post_count": len(items), "total_likes": total_likes,
                            "total_comments": total_comments}}
    except ImportError:
        import urllib.request
        fields = "message,created_time,likes.summary(true),comments.summary(true)"
        url = (f"https://graph.facebook.com/v18.0/{page_id}/posts"
               f"?fields={fields}&since={since}&limit=25&access_token={token}")
        resp = urllib.request.urlopen(url, timeout=30)
        data = json.loads(resp.read().decode())
        items, total_likes, total_comments = [], 0, 0
        for p in data.get("data", []):
            likes = p.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = p.get("comments", {}).get("summary", {}).get("total_count", 0)
            total_likes += likes
            total_comments += comments
            items.append({"id": p.get("id"), "message": p.get("message", "")[:100],
                          "created": p.get("created_time"), "likes": likes, "comments": comments})
        return {"status": "success", "platform": "facebook", "posts": items,
                "summary": {"post_count": len(items), "total_likes": total_likes,
                            "total_comments": total_comments}}


def main():
    ap = argparse.ArgumentParser(description="Facebook MCP – Gold Tier")
    ap.add_argument("--action", required=True, choices=["post", "fetch_activity"])
    ap.add_argument("--content", default="", help="Post content text")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    try:
        if args.action == "post":
            result = post_to_page(args.content, dry_run)
        else:
            result = fetch_activity(dry_run)
        log_event(f"fb_{args.action}", "social_facebook_mcp",
                  result.get("status", "success"),
                  details={"action": args.action, "social_post_id": result.get("post_id"),
                           "mcp_params": {"content": args.content[:50]}})
        print(json.dumps(result))
    except Exception as e:
        result = {"status": "error", "platform": "facebook", "error": str(e)}
        log_event(f"fb_{args.action}", "social_facebook_mcp", "failure",
                  details={"error": str(e)[:200]})
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
