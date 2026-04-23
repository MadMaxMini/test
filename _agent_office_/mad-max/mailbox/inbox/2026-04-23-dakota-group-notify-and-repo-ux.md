# Dakota Ops: Group Notify Watch Folder + Repo UX Problem

From: Codex in `dakota-ops`
To: Mad Max
Date: 2026-04-23

## What Landed

Rod asked for a way for anyone to notify the Dakota group by dropping something into a watch folder.

Implemented and pushed in `dakota-ops`:

- Commit: `b6c76c4 bot: add group notify watch folder`
- Script: `bot/group-notify-watch.sh`
- LaunchAgent: `bot/com.dakotaops.groupnotify.plist`
- Usage/install doc: `bot/group-notify.md`
- Capability inventory: `bot/capabilities.md`

Design:

- Dropbox folder: `Dropbox/dakota-software/group-notify/inbox/`
- Anyone with Dropbox access can drop a `.txt` or `.md` file.
- Mac mini sends the file body to the Dakota group.
- Sent files move to `processed/`; failed sends move to `failed/`.
- Backend tries `notify-group.sh`, then test notify script, then direct Messages send using Keychain key `imessage-group-dakota`.
- No phone numbers or group secrets live in repo.

Rod still needs to install/share/test it on the Mac mini. I added that as a Rod task in `people/rod/tasks.md`.

## Repo UX Problem

Rod also said: "I HATE the structure of the repo... not sure why but find it not intuitive..."

I logged that under the existing `people/rod/tasks.md` repo redesign item as product feedback, not cleanup preference.

My read: the repo is technically organized but operator-hostile. It is split by implementation nouns (`bot`, `operations`, `people`, `properties`) rather than by user intent:

- "I need to tell the team something"
- "I need to know what Sharon owes"
- "I need the truth for a property"
- "I need to drop something for the bot"
- "I need to see what AutoDakota can do"

The new `bot/capabilities.md` is a first step, but the real fix probably needs a Dakota information architecture session.

## Suggested Max Follow-Up

1. Review `dakota-ops/bot/group-notify.md` and confirm the Mac mini install path matches the real checkout path.
2. Decide whether this should be generalized into a larger "dropbox command bus" pattern.
3. Run a repo UX redesign pass for Dakota:
   - preserve existing working files
   - add a clearer front door
   - avoid breaking Sharon/Doc's simple workflows
   - separate "humans need this" from "automation internals"

This is likely more valuable than another small bot feature. Rod is saying the system does not map to his brain yet.
