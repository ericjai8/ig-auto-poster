# Instagram Auto-Poster

Fully automated fact-card posting via GitHub Actions. No server required.

## How it works
- `generate_facts_content.py` renders fact cards as images and adds them to `post_queue.json`.
- `ig_auto_post.py` posts the next queued item to Instagram, using this
  repo's own files (via raw.githubusercontent.com) as the public image URL
  Instagram's API requires.
- Two GitHub Actions workflows run these on a schedule — see `.github/workflows/`.

## One-time setup (see full walkthrough from Claude)
1. Push this repo to GitHub as a **public** repo (raw.githubusercontent.com
   URLs only work for public repos, unless you set up a different image host).
2. In repo Settings > Secrets and variables > Actions, add:
   - `IG_USER_ID` — your Instagram Business Account ID
   - `IG_ACCESS_TOKEN` — your long-lived Page access token
3. Confirm Actions are enabled (Settings > Actions > General).
4. Edit the `FACTS` list in `generate_facts_content.py` to your chosen niche.
5. Manually run the "Generate more content" workflow once (Actions tab) to
   seed the queue before the poster workflow's first scheduled run.

## Adjusting the schedule
Edit the `cron` lines in `.github/workflows/auto-post.yml`. Cron times are
always UTC.
