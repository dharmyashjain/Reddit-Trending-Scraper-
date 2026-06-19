# Reddit Trending Scraper
# Uses Reddit's public JSON API (no auth needed) to fetch trending posts
# from any subreddit. Displays title, score, comment count, and flair
# in a Rich table. Supports opening posts in the browser.
#
# Install: pip install requests rich
# Usage:   python reddit_scraper.py python
#          python reddit_scraper.py programming --sort top --limit 15

import requests
import argparse
import webbrowser
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
# Reddit requires a User-Agent header to avoid getting blocked
HEADERS = {"User-Agent": "reddit-cli-reader/1.0"}

def fetch_posts(subreddit, sort="hot", limit=10):
    # Reddit exposes public JSON data — just append .json to any URL
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    r = requests.get(url, headers=HEADERS, timeout=8)
    if r.status_code != 200:
        console.print(f"[red]Could not fetch r/{subreddit}. Check the name.[/red]")
        return []
    data = r.json()
    posts = []
    for child in data["data"]["children"]:
        p = child["data"]
        posts.append({
            "title": p["title"][:70] + ("..." if len(p["title"]) > 70 else ""),
            "score": p["score"],
            "comments": p["num_comments"],
            "flair": p.get("link_flair_text") or "",
            "url": "https://reddit.com" + p["permalink"],
            "nsfw": p.get("over_18", False)
        })
    return posts

def display(posts, subreddit, sort):
    table = Table(box=box.SIMPLE_HEAD, title=f"r/{subreddit} — {sort}")
    table.add_column("#", style="dim", width=3)
    table.add_column("Score", width=7, justify="right")
    table.add_column("Title", min_width=45)
    table.add_column("Comments", width=9, justify="right")
    table.add_column("Flair", width=14, style="dim")

    for i, p in enumerate(posts, 1):
        # Highlight high-score posts in green
        score_str = f"[green]{p['score']}[/green]" if p['score'] > 500 else str(p['score'])
        nsfw = " [red][nsfw][/red]" if p['nsfw'] else ""
        table.add_row(str(i), score_str, p["title"] + nsfw, str(p["comments"]), p["flair"])

    console.print(table)
    return posts

def main():
    parser = argparse.ArgumentParser(description="Reddit trending post scraper")
    parser.add_argument("subreddit", help="Subreddit name (without r/)")
    parser.add_argument("--sort", choices=["hot", "new", "top", "rising"], default="hot")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--open", type=int, help="Open post number in browser")
    args = parser.parse_args()

    posts = fetch_posts(args.subreddit, args.sort, args.limit)
    if posts:
        posts = display(posts, args.subreddit, args.sort)
        if args.open and 1 <= args.open <= len(posts):
            webbrowser.open(posts[args.open - 1]["url"])
        else:
            choice = console.input("[dim]Enter post number to open (or Enter to quit): [/dim]")
            if choice.isdigit() and 1 <= int(choice) <= len(posts):
                webbrowser.open(posts[int(choice) - 1]["url"])

if __name__ == "__main__":
    main()
