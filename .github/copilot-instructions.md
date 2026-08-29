# AI Agent Solution Instructions

## Objective
Build a self-driving AI developer system on Ubuntu VM using headless Visual Studio Code (`code-server`) with GitHub Copilot. The system should automatically process `.md` instruction files, implement requested code changes, push branches, and hand off QA instructions.

## High-Level Workflow
1. User places `.md` instruction file in `AI/AIAgentCoder/IN`.
2. Agent #1 (`AIAgentCoder`) picks up file and moves it to `AI/AIAgentCoder/PROCESSING`.
3. Agent #1 initializes a git repository if the target local path is missing.
4. Agent #1 creates a Git branch, opens workspace in `code-server`, processes markdown tasks, applies changes, runs build/tests, commits, and pushes to GitHub.
5. On success, markdown file is moved to `AI/AIAgentCoder/SUCCESS`; on failure, to `AI/AIAgentCoder/FAILURE`.
6. Agent #1 generates QA test-instruction markdown and writes it to `AI/AIAgentQA/IN`.
7. Agent #2 (`AIAgentQA`) processes QA instructions, runs Playwright and/or unit tests, commits/pushes test artifacts/results, and moves files to `SUCCESS` or `FAILURE`.

## Required Folder Structure
Create and use:

- `~/AI/AIAgentCoder/IN`
- `~/AI/AIAgentCoder/PROCESSING`
- `~/AI/AIAgentCoder/SUCCESS`
- `~/AI/AIAgentCoder/FAILURE`
- `~/AI/AIAgentQA/IN`
- `~/AI/AIAgentQA/PROCESSING`
- `~/AI/AIAgentQA/SUCCESS`
- `~/AI/AIAgentQA/FAILURE`
- `~/AI/Tasks`
- `~/AI/Data`

## Build Plan (Option B)

### Stage 1 — Install Dependencies on Ubuntu
1. Update system:
   - `sudo apt update && sudo apt upgrade -y`
2. Install Node.js and npm:
   - `sudo apt install -y nodejs npm`
3. Install Python and pip:
   - `sudo apt install -y python3 python3-pip`
4. Install GitHub CLI:
   - `type -p curl >/dev/null || sudo apt install curl -y`
   - `curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg`
   - `sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg`
   - `echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null`
   - `sudo apt update`
   - `sudo apt install gh -y`
5. Authenticate GitHub:
   - `gh auth login`

### Stage 2 — Install `code-server`
6. Install `code-server`:
   - `curl -fsSL https://code-server.dev/install.sh | sh`
7. Enable/start service:
   - `sudo systemctl enable --now code-server@$USER`
8. Access UI:
   - `http://localhost:8080`

### Stage 3 — Install GitHub Copilot in `code-server`
9. Install extensions:
   - GitHub Copilot
   - GitHub Copilot Chat
10. Authenticate in `code-server` when prompted.

### Stage 4 — Create Folder Structure
11. Run:
   - `mkdir -p ~/AI/AIAgentCoder/{IN,PROCESSING,SUCCESS,FAILURE}`
   - `mkdir -p ~/AI/AIAgentQA/{IN,PROCESSING,SUCCESS,FAILURE}`
   - `mkdir -p ~/AI/Tasks`
   - `mkdir -p ~/AI/Data`

### Stage 5 — Build Agent #1 (`AIAgentCoder`)
12. Install Python packages:
   - `pip install watchdog openai`
13. Create `~/AI/AIAgentCoder/agent.py` with:
   - folder watcher
   - markdown parser
   - git branch/commit/push automation
   - workspace automation through `code-server`
   - Copilot-chat task orchestration
   - build/test execution
   - file move lifecycle (IN → PROCESSING → SUCCESS/FAILURE)
   - QA instruction generation to `AIAgentQA/IN`

### Stage 6 — AI Backend / Copilot Chat Integration
14. Integrate chat backend so the agent can issue implementation instructions programmatically and validate changes.
15. Support backend choice based on environment (OpenAI API or Azure OpenAI, depending on deployment).

### Stage 7 — Build Agent #2 (`AIAgentQA`)
16. Install Playwright:
   - `npm install -D @playwright/test`
   - `npx playwright install`
17. Create `~/AI/AIAgentQA/agent.py` with:
   - watcher for `AIAgentQA/IN`
   - `.md` test instruction processing
   - Playwright/unit test generation and execution
   - git commit/push of QA results
   - lifecycle move logic to `PROCESSING`, `SUCCESS`, `FAILURE`

### Stage 8 — Run Agents as Services
18. Create systemd services:
   - `/etc/systemd/system/aiaentcoder.service`
   - `/etc/systemd/system/aiaentqa.service`
19. Enable/start services:
   - `sudo systemctl enable --now aiaentcoder`
   - `sudo systemctl enable --now aiaentqa`

### Stage 9 — Operating Model
20. Drop instruction file into `AI/AIAgentCoder/IN` (example: `loginFeature.md`).
21. Agent #1 implements and pushes branch, then creates QA instructions.
22. Agent #2 runs automated tests and pushes QA outcomes.

## Coding Style
- Python code must follow PEP 8.
- Type hints are required on public functions.
- Use `black` for formatting and `ruff` for linting.
- JavaScript/TypeScript (when used, including Playwright tooling) must use `eslint` and `prettier`.
- Keep functions small and single-purpose.
- Prefer configuration/constants over hardcoded paths.
- Do not keep commented-out dead code.

## Project Structure Rules
- Place Agent #1 implementation under `src/aia_coder/`.
- Place Agent #2 implementation under `src/aia_qa/`.
- Place shared utilities under `src/common/` (logging, filesystem helpers, git helpers, config).
- Place tests under `tests/unit/` and `tests/integration/`.
- Place operational scripts under `scripts/`.
- Keep runtime folders (`AI/AIAgentCoder/...`, `AI/AIAgentQA/...`) as data paths, not code paths.

## Required Validation Steps
Before any commit/push, all required checks must pass:

1. Lint and format checks pass.
2. Unit tests pass (`pytest`).
3. Integration/smoke tests for watcher and file lifecycle pass.
4. If UI/web changes exist, Playwright tests pass.

If any required check fails, fail fast, move the instruction file to `FAILURE`, and write an error summary.

## Branch and Commit Conventions
- Create one branch per instruction file.
- Branch naming:
  - `agent/coder/<timestamp>-<slug>`
  - `agent/qa/<timestamp>-<slug>`
- Never reuse branches across tasks.
- Use Conventional Commits (`feat:`, `fix:`, `test:`, `chore:`).
- Commit messages must include the instruction file name.
- Always push branches; never push directly to `main`.

## Forbidden Patterns and Tools
- No direct edits to `main` or `master`.
- No `git push --force` unless explicitly authorized.
- Do not store plaintext secrets/tokens in code or logs.
- Do not run destructive shell commands outside controlled temp paths.
- Do not skip tests to force a passing outcome.
- No silent failures; always record failure reasons and move files to `FAILURE`.
