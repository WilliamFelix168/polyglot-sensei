---
description: Fetch latest, stage, caveman-commit, push — one shot
argument-hint: optional note about the change
---

Run this flow in order, stopping if any step fails:

1. `git pull --rebase` (fetch + integrate latest from remote). If it conflicts, stop and report — do not force anything.
2. `git status` / `git diff` to see what changed. If nothing staged/unstaged, tell user and stop.
3. `git add -A` (review the file list first — abort and warn if anything looks like a secret: `.env`, keys, credentials).
4. Generate a commit message per the `caveman-commit` skill's rules (Conventional Commits, terse, subject <=50 chars, body only if the why isn't obvious). Use the user's note "$ARGUMENTS" as context for the why, if given.
5. `git commit -m "<generated message>"`.
6. `git push`.
7. Report the commit hash and one-line summary of what was pushed.
