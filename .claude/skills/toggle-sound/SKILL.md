---
name: sound
description: Toggle the task-completion sound on or off. Use when the user types /sound.
user_invocable: true
---

Toggle the task-completion sound chime.

Check if the flag file `~/.claude/skills/toggle-sound/sound-enabled` exists:
- If it exists, delete it and tell the user "Sound OFF"
- If it doesn't exist, create it and tell the user "Sound ON"

Use bash to check and toggle. Keep the response to one line.
