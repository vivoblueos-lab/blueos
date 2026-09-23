import json
import os
import sys
import urllib.request

repository = os.environ["GITHUB_REPOSITORY"]
pull_number = os.environ["PULL_NUMBER"]
token = os.environ["GITHUB_TOKEN"]
author = os.environ["PR_AUTHOR"]
head_sha = os.environ["PR_HEAD_SHA"]
sync_author = os.environ["SYNC_AUTHOR"]

if author == sync_author:
    print("Josh sync pull request detected; approval is not required.")
    raise SystemExit(0)

request = urllib.request.Request(
    f"https://api.github.com/repos/{repository}/pulls/{pull_number}/reviews?per_page=100",
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
)
with urllib.request.urlopen(request) as response:
    reviews = json.load(response)

approved = [
    review for review in reviews
    if review.get("state") == "APPROVED"
    and review.get("commit_id") == head_sha
]
if not approved:
    print("::error::Human pull requests require at least one approval on the latest head commit.", file=sys.stderr)
    raise SystemExit(1)

print("Human pull request approval requirement satisfied.")
