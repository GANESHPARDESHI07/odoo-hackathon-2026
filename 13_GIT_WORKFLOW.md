# 13 — GIT WORKFLOW

Optimized for one truth: **file ownership makes conflicts structurally impossible**, so git stays boring. Boring git wins hackathons.

## 1. Branch Model
```
main                     protected socially: Lead pushes only. Always installable.
├── feat/d1-fleet        Developer 1
├── feat/d2-drivers      Developer 2
├── feat/d3-trips        Developer 3
└── feat/d4-finance      Developer 4
hotfix/<name>            only after Feature Freeze (6:15), from main, merged by Lead
```
No other branches. No rebasing published branches (merge-only keeps everyone's Claude Code history sane).

## 2. Daily-driver commands (per dev)
```bash
git clone <repo> && cd <repo>
git checkout feat/d3-trips            # your branch, once, at Hour 0
git add -p && git commit              # small commits, message format below
git push                              # push at least every 30 min ("laptop dies" insurance)
# after every "MERGED" announcement:
git checkout feat/d3-trips && git pull origin main   # or: git merge main
```

## 3. Commit Convention
`<type>(<scope>): <BR-IDs if any> <summary>` — types: `feat`, `fix`, `chore`, `docs`, `test`. Scope = model/area. Examples:
`feat(trip): BR-06 BR-07 dispatch/complete automation` · `fix(vehicle): E-01 message text per contract` · `chore: hour-0 skeleton`.
One logical concern per commit; commit before any risky Claude-generated refactor so `git checkout -- <file>` is your undo button.

## 4. Merge Strategy (Lead only — full procedure `11` §2)
Checkpoint merges at 2:15 / 4:45 / 6:15, sequential `git merge --no-ff feat/d*`, install-test after each, tag after each window (`v0.1`, `v0.2`, `v1.0-rc`, final `v1.0`). PRs are optional ceremony: if organizers require them, open PRs at each window and the Lead self-merges after the checklist; otherwise local merges are faster and equally safe here.

## 5. Pre-Merge (a.k.a. PR) Checklist — dev side
- [ ] Only files I own are modified (`git diff --stat main...HEAD` shows nothing foreign)
- [ ] `-u transitops` clean on my machine; regression mini-list (`12` §I) green
- [ ] Error texts verbatim E-xx; BR-IDs cited in code
- [ ] `17` status + `18` merge note posted
- [ ] Branch pushed

## 6. Review Checklist — Lead side (60 seconds per branch)
- [ ] `git diff --stat` touches only owned files (frozen files untouched)
- [ ] No new deps, no manifest edits, no `sudo()`, no prints
- [ ] Install test passes post-merge
- [ ] Spot-check one BR behavior from the dev's scope

## 7. Conflict Resolution Protocol
Conflicts should not occur; when one does: identify the file's owner (`00` §3) → owner's hunks win → other party re-applies their need as a request. Frozen-file conflict → Lead's `main` version wins unconditionally. Never resolve by guessing; never `--force` push anything, ever. If a merge turns messy: `git merge --abort`, take the branches one file at a time with `git checkout <branch> -- <owned files>`, commit manually (this is `21` §4).

## 8. After Feature Freeze (6:15)
Only `fix(...)` commits via `hotfix/*` branches off `main`, merged by Lead immediately after a targeted retest. Feature commits after freeze are reverted without discussion — demo stability outranks any feature.
