# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""X/Twitter MCP: posts tweets and fetches recent activity via API v2.
Usage: python social_x_mcp.py --action {post,fetch_activity} [--content <text>] [--dry-run]

Note: Posting requires paid Basic tier. If posting fails due to access level,
falls back to creating a draft file in Plans/ with manual posting note."""
import argparse, json, os, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from log_utils import log_event

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

VAULT = Path(__file__).parent / "AI_Employee_Vault"


def get_config():
    api_key = os.environ.get("X_API_KEY", "")
    api_secret = os.environ.get("X_API_SECRET", "")
    access_token = os.environ.get("X_ACCESS_TOKEN", "")
    access_secret = os.environ.get("X_ACCESS_TOKEN_SECRET", "")
    if not all([api_key, api_secret, access_token, access_secret]):
        raise RuntimeError("X API credentials must be set in .env: "
                           "X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET")
    return api_key, api_secret, access_token, access_secret


def post_tweet(content, dry_run=False):
    """Post a tweet via X API v2."""
    if len(content) > 280:
        content = content[:277] + "..."
    if dry_run:
        return {"status": "dry_run", "platform": "x", "content": content}
    api_key, api_secret, access_token, access_secret = get_config()
    try:
        import tweepy
        client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret,
                               access_token=access_token, access_token_secret=access_secret)
        result = client.create_tweet(text=content)
        tweet_id = result.data.get("id", "") if result.data else ""
        return {"status": "posted", "platform": "x", "post_id": tweet_id,
                "content": content}
    except ImportError:
        return _post_tweet_oauth1(content, api_key, api_secret, access_token, access_secret)
    except Exception as e:
        if "403" in str(e) or "access" in str(e).lower():
            return _create_draft_fallback(content, str(e))
        raise


def _post_tweet_oauth1(content, api_key, api_secret, access_token, access_secret):
    """Post via requests-oauthlib as fallback."""
    try:
        from requests_oauthlib import OAuth1Session
        session = OAuth1Session(api_key, client_secret=api_secret,
                                resource_owner_key=access_token,
                                resource_owner_secret=access_secret)
        resp = session.post("https://api.twitter.com/2/tweets",
                            json={"text": content})
        if resp.status_code == 201:
            data = resp.json()
            return {"status": "posted", "platform": "x",
                    "post_id": data.get("data", {}).get("id", ""),
                    "content": content}
        elif resp.status_code == 403:
            return _create_draft_fallback(content, f"HTTP 403: {resp.text[:200]}")
        else:
            raise RuntimeError(f"X API error {resp.status_code}: {resp.text[:200]}")
    except ImportError:
        return _create_draft_fallback(content, "Neither tweepy nor requests-oauthlib installed")


def _create_draft_fallback(content, reason):
    """Create a draft file in Plans/ when posting is not available."""
    now = datetime.now(timezone(timedelta(hours=5)))
    fname = f"XDraft_{now.strftime('%Y%m%d_%H%M%S')}.md"
    path = VAULT / "Plans" / fname
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntype: x_draft\ncreated: {now.isoformat()}\nstatus: manual_required\n---\n\n"
        f"# X/Twitter Draft — Manual Posting Required\n\n"
        f"**Reason**: {reason}\n\n"
        f"## Tweet Text\n\n{content}\n\n"
        f"**Note**: X API paid tier not available. Please post this manually.\n",
        encoding="utf-8")
    log_event("x_draft_fallback", "social_x_mcp", "success",
              details={"reason": reason[:100], "draft_path": f"Plans/{fname}"})
    return {"status": "draft_fallback", "platform": "x", "draft_path": f"Plans/{fname}",
            "content": content, "reason": reason[:100]}


def fetch_activity(dry_run=False):
    """Fetch recent tweets and engagement (last 7 days)."""
    if dry_run:
        return {"status": "dry_run", "platform": "x", "tweets": [],
                "summary": {"tweet_count": 0, "total_likes": 0, "total_retweets": 0}}
    api_key, api_secret, access_token, access_secret = get_config()
    try:
        import tweepy
        client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret,
                               access_token=access_token, access_token_secret=access_secret)
        me = client.get_me()
        user_id = me.data.id if me.data else None
        if not user_id:
            return {"status": "error", "platform": "x", "error": "Could not get user ID"}
        start = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat().replace("+00:00", "Z")
        tweets = client.get_users_tweets(user_id, start_time=start, max_results=25,
                                          tweet_fields=["public_metrics", "created_at"])
        items, total_likes, total_rts = [], 0, 0
        for t in (tweets.data or []):
            metrics = t.public_metrics or {}
            likes = metrics.get("like_count", 0)
            rts = metrics.get("retweet_count", 0)
            total_likes += likes
            total_rts += rts
            items.append({"id": t.id, "text": t.text[:100], "created": str(t.created_at),
                          "likes": likes, "retweets": rts})
        return {"status": "success", "platform": "x", "tweets": items,
                "summary": {"tweet_count": len(items), "total_likes": total_likes,
                            "total_retweets": total_rts}}
    except ImportError:
        return {"status": "error", "platform": "x",
                "error": "tweepy not installed — cannot fetch activity"}
    except Exception as e:
        return {"status": "error", "platform": "x", "error": str(e)[:200]}


def main():
    ap = argparse.ArgumentParser(description="X/Twitter MCP – Gold Tier")
    ap.add_argument("--action", required=True, choices=["post", "fetch_activity"])
    ap.add_argument("--content", default="", help="Tweet text (max 280 chars)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "").lower() == "true"
    try:
        if args.action == "post":
            result = post_tweet(args.content, dry_run)
        else:
            result = fetch_activity(dry_run)
        log_event(f"x_{args.action}", "social_x_mcp", result.get("status", "success"),
                  details={"action": args.action, "social_post_id": result.get("post_id"),
                           "mcp_params": {"content": args.content[:50]}})
        print(json.dumps(result))
    except Exception as e:
        result = {"status": "error", "platform": "x", "error": str(e)}
        log_event(f"x_{args.action}", "social_x_mcp", "failure",
                  details={"error": str(e)[:200]})
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
