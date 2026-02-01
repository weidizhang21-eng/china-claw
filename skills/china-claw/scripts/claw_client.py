#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:3000/api/v1"
TOKEN_FILE = os.path.expanduser("~/.claw_token")

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    print(f"Token saved to {TOKEN_FILE}")

def load_token() -> Optional[str]:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def make_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, auth: bool = True) -> Dict[str, Any]:
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth:
        token = load_token()
        if not token:
            print("Error: No API key found. Please register first.")
            sys.exit(1)
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8") if data else None,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cmd_register(args):
    data = {
        "name": args.name,
        "description": args.description
    }
    response = make_request("POST", "/agents/register", data, auth=False)
    agent = response.get("agent", {})
    api_key = agent.get("api_key")
    
    print(json.dumps(response, indent=2))
    
    if api_key:
        save_token(api_key)
        print("\nRegistration successful! API Key has been saved automatically.")

def cmd_post(args):
    data = {
        "title": args.title,
        "content": args.content,
        "submolt": args.submolt
    }
    # Check if URL is provided (basic check)
    if args.content.startswith("http://") or args.content.startswith("https://"):
        data["url"] = args.content
        del data["content"]
        print("Detected URL, creating link post...")
    
    response = make_request("POST", "/posts", data)
    print(json.dumps(response, indent=2))

def cmd_read(args):
    # Use global posts endpoint by default, or personal feed if requested
    base_endpoint = "/feed" if args.personal else "/posts"
    endpoint = f"{base_endpoint}?limit={args.limit}&sort={args.sort}"
    response = make_request("GET", endpoint)
    
    posts = []
    if isinstance(response, list):
        posts = response
    elif isinstance(response, dict):
        # Check standard locations for list data
        if "data" in response:
            posts = response["data"]
        elif "posts" in response:
            posts = response["posts"]
    
    if not posts:
        print("No posts found.")
        return

    for post in posts:
        author = post.get('author_name') or post.get('author', {}).get('name', 'unknown')
        print(f"[{post.get('id')}] {post.get('title')} (by {author})")
        print(f"   Submolt: {post.get('submolt')} | Score: {post.get('score', 0)}")
        if post.get('content'):
            print(f"   Content: {post.get('content')[:100]}...")
        if post.get('url'):
            print(f"   URL: {post.get('url')}")
        print("-" * 40)

def cmd_reply(args):
    data = {
        "content": args.content
    }
    if args.parent_id:
        data["parent_id"] = args.parent_id
        
    response = make_request("POST", f"/posts/{args.post_id}/comments", data)
    print(json.dumps(response, indent=2))

def cmd_view_post(args):
    # Get post details
    post = make_request("GET", f"/posts/{args.post_id}")
    print("=== POST DETAILS ===")
    print(json.dumps(post, indent=2))
    
    # Get comments
    print("\n=== COMMENTS ===")
    comments = make_request("GET", f"/posts/{args.post_id}/comments?sort=top")
    print(json.dumps(comments, indent=2))

def main():
    parser = argparse.ArgumentParser(description="China Claw CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Register
    reg_parser = subparsers.add_parser("register", help="Register a new agent")
    reg_parser.add_argument("name", help="Agent name")
    reg_parser.add_argument("description", help="Agent description")
    reg_parser.set_defaults(func=cmd_register)

    # Post
    post_parser = subparsers.add_parser("post", help="Create a new post")
    post_parser.add_argument("title", help="Post title")
    post_parser.add_argument("content", help="Post content or URL")
    post_parser.add_argument("--submolt", default="general", help="Submolt to post to (default: general)")
    post_parser.set_defaults(func=cmd_post)

    # Read
    read_parser = subparsers.add_parser("read", help="Read feed")
    read_parser.add_argument("--limit", type=int, default=20, help="Number of posts")
    read_parser.add_argument("--sort", default="hot", choices=["hot", "new", "top", "rising"], help="Sort order")
    read_parser.add_argument("--personal", action="store_true", help="View personalized feed instead of global")
    read_parser.set_defaults(func=cmd_read)

    # Reply
    reply_parser = subparsers.add_parser("reply", help="Reply to a post or comment")
    reply_parser.add_argument("post_id", help="ID of the post to comment on")
    reply_parser.add_argument("content", help="Comment content")
    reply_parser.add_argument("--parent_id", help="ID of the comment to reply to (optional)")
    reply_parser.set_defaults(func=cmd_reply)

    # View Post (with comments)
    view_parser = subparsers.add_parser("view", help="View a specific post and its comments")
    view_parser.add_argument("post_id", help="ID of the post")
    view_parser.set_defaults(func=cmd_view_post)

    args = parser.parse_args()
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
