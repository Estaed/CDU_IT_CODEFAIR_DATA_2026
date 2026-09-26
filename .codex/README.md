# `.codex/` in this project — what belongs here, and what deliberately does not

Codex reads three things. Only one of them is project-local:

| What | Where it comes from | Project-local? |
| --- | --- | --- |
| Project instructions | `AGENTS.md` at the repo root | **yes** — generated from `CLAUDE.md` |
| Skills | `~/.codex/skills/` (junctions to `D:\TarikOS\.claude\skills\`) | no — user scope, one source |
| Slash commands | `~/.codex/prompts/*.md` (generated stubs, one per skill) | no — user scope, one source |

So there is no `.codex/skills/` and no `.codex/commands/` here, and adding them
would be a regression: a project-local copy shadows the vault version silently,
and the shadow does not announce itself — it just serves a stale skill forever.
Same reason `.claude/skills-README.md` says the same thing on the Claude side.

`.claude/commands/*.md` **is** local, and that is not an inconsistency: those files
do not shadow a skill, they only invoke one. Codex has no project-level equivalent,
which is why the same shortcuts live in `~/.codex/prompts/`.

## Keeping both CLIs in sync

    python D:\TarikOS\.brain\scripts\mount_skills.py            # repair links + regenerate prompts
    python D:\TarikOS\.brain\scripts\mount_skills.py --check    # audit only, exit 1 if anything is missing

Run it after writing a new skill in the vault. A skill that exists but is not
mounted does not error — it simply never gets called, which is the hardest kind
of failure to notice.

## Hooks

Codex memory and rule hooks now live in the user-level `~/.codex/hooks.json`.
This project does not keep a second `.codex/hooks.json`. To audit the user-level
hooks, run `python D:/TarikOS/.brain/scripts/render_codex_hooks.py --user --check`.
The script's `--project .` mode removes obsolete project hook entries; it does not
generate a project hook file.
