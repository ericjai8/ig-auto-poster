# Instagram Auto-Poster

Fully automated fact-card posting via GitHub Actions. No server required.

## Current status
- Posting pipeline ( + GitHub Actions) is set up and ready 
- Focused on generating a starter batch of 50-100 high-quality facts to seed the queue
- Template-based card design for now; custom illustrations per fact are a future possibility

## How it works
-  renders fact cards as images and adds them to .
-  posts the next queued item to Instagram, using this 
  repo's own files (via raw.githubusercontent.com) as the public image URL
  Instagram's API requires.
- Two GitHub Actions workflows run these on a schedule — see .

## Next steps 
1. Decide on a niche/topic for the fact cards (e.g. psychology, history, space)
2. Generate a diverse batch of 50-100 facts in that niche
3. Tweak the card design (colors, layout, fonts) to match the niche
4. Let the auto-poster run and focus on community engagement!

## Adjusting the schedule
Edit the  lines in . Cron times are
always UTC.
