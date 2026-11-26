# Task 3 Report

GitHub Copilot in VS Code supports `AGENTS.md`. My initiating prompt was “do this task,” with `Task_3.md` as context; I then asked Copilot to inspect the repository, check official support, create the instruction files, and write this report. I did not use a slash command. I reviewed the result and later edited `Assignments/AGENTS.md` to remove repetition and add concise-English report guidance; the root `AGENTS.md` was not changed afterward.

VS Code documents `/init` for Local agent sessions. In the Copilot harness, only `/prompts` and `/hooks` are available among the customization commands. I tried to focus the chat input to test `/ini`, but VS Code detected active user input and interrupted the click; I could not type it or verify the suggestions firsthand.

References:
- [VS Code: Use custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
- [VS Code: Custom instructions reference](https://code.visualstudio.com/docs/agents/reference/custom-instructions-reference)
- [VS Code: AI features cheat sheet](https://code.visualstudio.com/docs/agents/reference/ai-features-cheat-sheet)
