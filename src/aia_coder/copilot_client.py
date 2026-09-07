from __future__ import annotations

import json
from typing import Any

from openai import AzureOpenAI, OpenAI

from src.common.config import load_ai_settings
from src.common.models import AISettings, FileChange, TaskResponse


class CopilotClient:
    def __init__(self, settings: AISettings | None = None, client: Any | None = None) -> None:
        self.settings = settings or load_ai_settings()
        self._client = client or self._create_client()

    def ask(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.settings.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return only JSON matching this schema: "
                        "{summary: string, changes: [{operation: 'create'|'update'|'delete', "
                        "path: string, content: string|null}], validation_commands: string[]}. "
                        "The changes value must be an array, never an object or string."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or "{}"

    def ask_for_task(self, prompt: str) -> TaskResponse:
        try:
            payload = json.loads(self.ask(prompt))
            raw_changes = payload.get("changes", [])
            if not isinstance(raw_changes, list):
                raise ValueError("changes must be a list of file change objects.")
            changes = []
            for item in raw_changes:
                if not isinstance(item, dict):
                    raise ValueError("Each change must be an object.")
                changes.append(FileChange(item["operation"], item["path"], item.get("content")))
            commands = payload.get("validation_commands", [])
            if not isinstance(commands, list) or not all(isinstance(item, str) for item in commands):
                raise ValueError("validation_commands must be a list of strings.")
            return TaskResponse(str(payload.get("summary", "")), changes, commands)
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("AI response was not valid structured task JSON.") from exc

    def _create_client(self) -> Any:
        if self.settings.backend == "openai":
            return OpenAI(api_key=self.settings.api_key)
        return AzureOpenAI(api_key=self.settings.api_key, azure_endpoint=self.settings.endpoint, api_version=self.settings.api_version)
