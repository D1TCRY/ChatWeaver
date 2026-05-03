# chatweaver

A Python library that simplifies building AI-driven chatbots with OpenAI, offering conversation management, long-form generation, file attachments, structured outputs, and persistent storage in one cohesive package.

## Overview

### What it is

`chatweaver` is a Python library for building chatbots on top of OpenAI, with:

* A `Model` wrapper for OpenAI client access and lazy API key validation
* A `Bot` abstraction for creating chat completions, including optional images, file attachments, structured outputs, and long-form output controls
* A `Chat` session that manages conversation history and reply limits
* A `Schema` helper to request structured JSON outputs
* An `Archive` format (`.cwarchive`) for saving/loading `Model`, `Bot`, `Chat`, and `TextNode` objects
* Configurable system rules, output formatting, language behavior, and model-name presets

### Why it exists / main value

It provides a cohesive set of building blocks to:

* Manage conversations with history
* Generate short answers, long-form text, or long code outputs
* Attach images and upload files to OpenAI
* Persist and restore bots/chats/models, with secrets excluded by default
* Keep prompt rules, model names, schemas, and chat state organized in Python objects

### Key features

* Conversation management via `Chat` with message history (`TextNode`) and reply limits
* OpenAI model wrapper with lazy API key validation (`Model`)
* Long-form generation controls via `Bot`:

  * `max_completion_tokens=None` by default, so ChatWeaver does not impose an output-token cap
  * Optional `max_completion_tokens` to set an explicit upper bound
  * Optional `auto_continue` to continue automatically when the model stops because of length
  * `finish_reason` and `continuations` returned in `BotCompletionResult`
* Support for attachments:

  * Images from local paths or URLs
  * Files from local paths, existing file IDs, or OpenAI `FileObject`s
* Structured outputs via `Schema` (`response_format` JSON schema)
* Persistence to a binary `.cwarchive` file via `Archive` (atomic save + integrity checks)
* Freeze/thaw snapshots for `Model`, `Bot`, `Chat`, `Schema`, and `TextNode`
* Built-in prompt presets through `ChatWeaverSystemRules`
* Built-in and extensible model names through `ChatWeaverModelNames`

### Typical use cases

* Build an OpenAI-powered chatbot with managed conversation history
* Generate long articles, documentation, reports, or complete code files
* Add image inputs to a prompt
* Upload local files and attach them to a request
* Request strict JSON outputs using a schema
* Enforce a rolling chat history using a reply limit
* Save and restore chat sessions/bots/models without storing API keys by default

## Installation

### Requirements

* Python >= 3.10
* OS Independent
* Dependency:

  * `openai==2.3.0`

### Install via pip

```bash
pip install chatweaver
```

## Quickstart

### Minimal working example

The code below demonstrates creating a chat session and generating a response.

```python
from chatweaver import Model, Bot, Chat

# Provide your API key to enable remote services
model = Model(api_key="TODO: set your OpenAI API key", model="gpt-4o")

bot = Bot(model=model, name="AI Bot")
chat = Chat(bot=bot, title="New Chat", user="User", replies_limit=10)

reply = chat.response("Hello! What can you do?")
print(reply)
```

## Long-form outputs

`Bot` is designed to avoid limiting the response length from the library side.

By default, `max_completion_tokens=None`, which means ChatWeaver does not send a `max_completion_tokens` cap to OpenAI. This is the closest API behavior to “let the model answer as fully as it can”. The response is still not infinite: it remains limited by the selected model, the available context window, API behavior, safety behavior, and the model’s own decision to stop.

For long text or long code generation, combine three things:

* Use a model with a large enough context/output capacity.
* Ask explicitly for a complete, non-abbreviated answer in the prompt.
* Enable `auto_continue` if you want ChatWeaver to continue after a length stop.

### Example: long output bot

```python
from chatweaver import Model, Bot

model = Model(api_key="TODO: set your OpenAI API key", model="gpt-4o")

bot = Bot(
    model=model,
    max_completion_tokens=None,  # default: no output cap sent by ChatWeaver
    auto_continue=True,          # continue if the model stops because of length
    max_continuations=3,         # safety limit for extra continuation calls
)

result = bot.completion(
    "Write a complete Python module for a small task manager. "
    "Do not omit code. Do not use placeholders."
)

print(result.content)
print("Finish reason:", result.finish_reason)
print("Continuations used:", result.continuations)
```

### Example: set an explicit output cap

Use `max_completion_tokens` when you want to keep cost and output size bounded.

```python
from chatweaver import Model, Bot

model = Model(api_key="TODO: set your OpenAI API key")
bot = Bot(model=model, max_completion_tokens=1200)

result = bot.completion("Explain decorators in Python with examples.")
print(result.content)
```

### Example: override output settings per request

`Bot` stores default generation settings, but `completion()` can override them for one call.

```python
result = bot.completion(
    prompt="Generate a complete README for this package.",
    max_completion_tokens=None,
    auto_continue=True,
    max_continuations=2,
)
```

### Notes about automatic continuation

When `auto_continue=True`, ChatWeaver checks whether the response stopped with `finish_reason == "length"`. If so, it appends the partial assistant response to the message list and sends a follow-up instruction asking the model to continue exactly where it stopped.

`max_continuations` controls how many extra calls are allowed. This prevents accidental long loops and gives you predictable cost boundaries.

`auto_continue` is not compatible with `response_schema`, because splitting a strict structured JSON response across multiple independent calls can produce invalid JSON. If you need structured output, keep the schema response in a single call or design a chunked schema workflow manually.

## Usage examples

### 1) Use `Chat` with rolling history (reply limit)

`Chat` stores history as `TextNode` pairs (user + assistant). When the reply limit is reached, the oldest pair is dropped.

```python
from chatweaver import Model, Bot, Chat

model = Model(api_key="TODO: set your OpenAI API key")
bot = Bot(model=model, name="AI Bot")
chat = Chat(bot=bot, replies_limit=2)

print(chat.response("First message"))
print(chat.response("Second message"))
print(chat.response("Third message (oldest pair will be dropped)"))

print("Replies:", chat.replies)
print("Token cost (sum of stored nodes):", chat.cost)
```

### 2) Use `Chat` with a long-output bot

`Chat.response()` uses the configured `Bot`. To make all chat replies long-output friendly, configure the `Bot` before passing it to `Chat`.

```python
from chatweaver import Model, Bot, Chat

model = Model(api_key="TODO: set your OpenAI API key")

bot = Bot(
    model=model,
    max_completion_tokens=None,
    auto_continue=True,
    max_continuations=2,
)

chat = Chat(bot=bot, replies_limit=5)

reply = chat.response(
    "Write a complete implementation plan for a small web app. "
    "Be detailed and do not abbreviate sections."
)

print(reply)
```

### 3) Request structured output with `Schema`

`Schema.resolve()` produces an OpenAI-compatible `response_format` with `json_schema` and `strict=True`.

```python
from chatweaver import Model, Bot, Schema

schema = Schema(
    name="AnswerSchema",
    properties={
        "answer": {"type": "string"},
        "confidence": {"type": "number"},
    },
)

model = Model(api_key="TODO: set your OpenAI API key")
bot = Bot(model=model, schema=schema)

result = bot.completion("Explain what JSON Schema is in one sentence.")
print(result.content)
```

### 4) Attach images (URL or local path)

Images can be:

* URLs (must be valid URL)
* Local paths (converted to `data:image/png;base64,...`)

```python
from chatweaver import Model, Bot

model = Model(api_key="TODO: set your OpenAI API key")
bot = Bot(model=model)

# URL-based image
result = bot.completion(
    prompt="Describe what you see in the image.",
    img_data="https://example.com/some-image.png",
)
print(result.content)

# Local image path (embedded as base64 data URL)
result = bot.completion(
    prompt="Describe what you see in the image.",
    img_data="TODO: path/to/local-image.png",
)
print(result.content)
```

### 5) Attach files (local path upload or file_id)

Files can be:

* A file ID (already uploaded)
* A local path (uploaded via the OpenAI Files API with `purpose="user_data"`)
* An OpenAI `FileObject`
* URLs are **not supported** for files and will raise `ValueError`

```python
from chatweaver import Model, Bot

model = Model(api_key="TODO: set your OpenAI API key")
bot = Bot(model=model)

# Attach a file_id (already uploaded elsewhere)
result = bot.completion(
    prompt="Summarize the attached document.",
    file_data="TODO: existing-file-id",
)
print(result.content)

# Attach a local file path (will be uploaded)
result = bot.completion(
    prompt="Summarize the attached document.",
    file_data="TODO: path/to/document.pdf",
)
print(result.content)
```

## API Reference

### Package exports

The top-level package exports:

* `Schema`
* `TextNode`
* `Model`
* `Bot`
* `Chat`
* `Archive`
* `ChatWeaverModelNames`, `ChatWeaverSystemRules`, `Formatting`, `Language`

```python
from chatweaver import (
    Schema,
    TextNode,
    Model,
    Bot,
    Chat,
    Archive,
    ChatWeaverModelNames,
    ChatWeaverSystemRules,
    Formatting,
    Language,
)
```

### `Model`

Wrapper around OpenAI client access with lazy validation.

```python
class Model:
    def __init__(self, api_key: Optional[str] = None, model: str = ChatWeaverModelNames.gpt_4o, **kwargs) -> None: ...
    def freeze(self, include_secrets: bool = False) -> dict[str, Any]: ...
    @classmethod
    def thaw(cls, snapshot: dict[str, Any], api_key: Optional[str] = None) -> "Model": ...
    def api_key_hint(self) -> str: ...
    def validate_api_key(self) -> bool: ...
    @property
    def client(self) -> openai.OpenAI: ...
    def can_use_remote_services(self) -> bool: ...
```

#### Notes

* `api_key` is not validated when assigned. It is validated when `client` is accessed.
* If the API key format is invalid, `key_status` becomes `INVALID` and `last_auth_error` is set.
* Accessing `client` when the key cannot be validated raises `RuntimeError` with the reason.
* `freeze(include_secrets=False)` does not store the API key by default.

### `Bot`

Conversational bot that uses a `Model` instance.

```python
class Bot:
    def __init__(
        self,
        model: Optional[Model] = None,
        rules: Optional[str] = ChatWeaverSystemRules.default(),
        name: str = "AI Bot",
        schema: Optional[Schema] = None,
        time_format: str = "%d/%m/%Y %H:%M:%S",
        max_completion_tokens: Optional[int] = None,
        auto_continue: bool = False,
        max_continuations: int = 0,
        **kwargs,
    ) -> None: ...

    def freeze(self, include_secrets: bool = False) -> dict[str, Any]: ...
    @classmethod
    def thaw(
        cls,
        snapshot: dict[str, Any],
        model: Optional[Model] = None,
        api_key: Optional[str] = None,
    ) -> "Bot": ...

    def completion(
        self,
        prompt: str,
        user: str = "User",
        history: list | None = None,
        img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
        file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None,
        response_schema: Schema | None = None,
        max_completion_tokens: Optional[int] = None,
        auto_continue: Optional[bool] = None,
        max_continuations: Optional[int] = None,
    ) -> "BotCompletionResult": ...
```

#### Parameters

* `prompt`: The user prompt string.
* `user`: Name of the user. It is included in the system prompt.
* `history`: Optional message list prepended to the constructed system/user messages. ChatWeaver normalizes history into OpenAI-compatible messages before sending it.
* `img_data`:

  * `str`/`pathlib.Path`: a single image URL or local path
  * `list[str|pathlib.Path]`: multiple image URLs/paths
  * Local paths are base64-encoded into a `data:image/png;base64,...` URL.
* `file_data`:

  * `str`/`pathlib.Path`: a local path or file ID string
  * `FileObject`: OpenAI file object
  * `list[...]`: multiple local paths / file IDs / `FileObject`s
  * URLs are **not supported** for files.
* `response_schema`: A `Schema` to use for this request. If omitted, `Bot.schema` is used.
* `max_completion_tokens`: Optional output-token cap for the current call. If `None`, ChatWeaver does not send a cap.
* `auto_continue`: Optional per-call override for automatic continuation after `finish_reason == "length"`.
* `max_continuations`: Optional per-call override for the number of automatic continuation calls.

#### Returns

* `BotCompletionResult` containing:

  * `content` (assistant message content or refusal)
  * token usage (`prompt_tokens`, `completion_tokens`, `total_tokens`)
  * timestamps (`start_date`, `final_date`) and timing (`delta_time`)
  * input/output metadata (`MetadataContainer`)
  * `finish_reason` from the final OpenAI response
  * `continuations`, the number of automatic continuation calls used

#### Raised exceptions (selected)

* `TypeError` if `img_data`, `file_data`, `response_schema`, or token settings are invalid
* `ValueError` if an image path/URL is invalid, if `file_data` is a URL, if token values are invalid, or if `auto_continue` is used with a structured schema
* `RuntimeError` from `Model.client` if remote services are not available due to missing/invalid key
* Other exceptions may bubble up from the OpenAI client

### `BotCompletionResult`

Immutable result object returned by `Bot.completion()`.

```python
@dataclass(frozen=True)
class BotCompletionResult:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    start_date: str
    delta_time: float
    final_date: str
    input_metadata: MetadataContainer
    output_metadata: MetadataContainer
    finish_reason: str | None = None
    continuations: int = 0
```

#### Notes

* `finish_reason` tells you why the final model response stopped.
* `continuations` tells you how many extra calls were used by `auto_continue`.
* Token usage is accumulated across the original request and all automatic continuations.

### `Chat`

Chat session that keeps history and uses a `Bot`.

```python
class Chat:
    def __init__(
        self,
        bot: Optional[Bot] = None,
        title: str = "New Chat",
        replies_limit: int | None = 10,
        user: str = "User",
        time_format: str = "%d/%m/%Y %H:%M:%S",
        creation_date: Optional[str] = None,
        history: Optional[list[TextNode] | list[dict[str, Any]]] = None,
        **kwargs,
    ) -> None: ...

    def freeze(self, include_secrets: bool = False) -> dict[str, Any]: ...
    @classmethod
    def thaw(
        cls,
        snapshot: dict[str, Any],
        bot: Optional[Bot] = None,
        api_key: Optional[str] = None,
    ) -> "Chat": ...

    def response(
        self,
        prompt: str,
        user: Optional[str] = None,
        image_path: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> str: ...

    @property
    def replies(self) -> int: ...
    @property
    def cost(self) -> int: ...
```

#### Notes

* `replies_limit=None` means no reply limit.
* `history` accepts:

  * `list[TextNode]`
  * `list[dict]` (either frozen snapshots or plain dict payloads)
* `response()` appends a user `TextNode` and an assistant `TextNode` to history.
* When the reply limit is reached, the oldest user/assistant pair is dropped.
* Long-output behavior is controlled by the `Bot` used by the chat.

### `Archive`

Persistence for `Chat`, `Bot`, `Model`, and `TextNode` to a binary `.cwarchive` file.

```python
class Archive:
    def __init__(self, path: str, api_key: str | None = None, asynchronous: bool = True, delay: float = 0.07) -> None: ...

    @property
    def data(self) -> dict[int, Chat | Bot | Model]: ...

    def add(self, element: Chat | Bot | Model) -> None: ...
    def remove(self, element: list | tuple | int | Chat | Bot | Model, remove_type: str = "all") -> None: ...
    def save(self, path: str | None = None, include_secrets: bool = False) -> None: ...

    def retrieve(
        self,
        path: str | None = None,
        api_key: str | None = None,
        api_key_provider: Optional[Callable[[int, int, dict[str, Any]], Optional[str]]] = None,
    ) -> dict[int, Any]: ...
```

#### Notes

* `Archive.path` ensures parent directories exist and creates an empty file if missing.
* `save(include_secrets=False)` writes snapshots without API keys by default.
* `retrieve(..., api_key=..., api_key_provider=...)` can inject API keys during restoration.
* When `asynchronous=True`, object reconstruction uses `asyncio` + `asyncio.to_thread`.

### `Schema`

A JSON schema container for structured model outputs.

```python
@dataclass(frozen=True)
class Schema:
    name: str
    properties: dict[str, Any]

    @property
    def required(self) -> list[str]: ...
    def resolve(self) -> dict: ...
    def freeze(self) -> dict[str, Any]: ...
    @classmethod
    def thaw(cls, snapshot: dict[str, Any]) -> "Schema": ...
```

#### Notes

* All provided properties are marked as required.
* `additionalProperties` is set to `False`.
* `strict=True` is used in the resolved OpenAI response format.

### `TextNode`

Immutable message node with metadata.

```python
@dataclass(frozen=True)
class TextNode:
    role: str
    content: str
    owner: str
    tokens: int
    date: str
    image_data: list[Any]
    file_data: list[Any]

    def freeze(self) -> dict[str, Any]: ...
    @classmethod
    def thaw(cls, snapshot: dict[str, Any]) -> "TextNode": ...
```

## Configuration

### `ChatWeaverModelNames`

`ChatWeaverModelNames` is a controlled registry of model-name strings.

It exists for two reasons:

* To avoid scattering raw model strings across your codebase.
* To let `Model.model` validate that the selected model name is one of the names known by ChatWeaver.

Built-in fields include:

* `gpt_4` -> `"gpt-4"`
* `gpt_4o` -> `"gpt-4o"`
* `gpt_4_turbo` -> `"gpt-4-turbo"`
* `o1` -> `"o1"`
* `o1_mini` -> `"o1-mini"`
* `o3` -> `"o3"`

```python
from chatweaver import ChatWeaverModelNames

print(ChatWeaverModelNames.gpt_4o)
print(ChatWeaverModelNames.get_all_models())
```

The object is locked against direct attribute assignment/deletion. This keeps the registry predictable:

```python
ChatWeaverModelNames.gpt_4o = "other-model"  # raises SyntaxError
```

To extend the registry, use `add()`:

```python
from chatweaver import ChatWeaverModelNames, Model

ChatWeaverModelNames.add("gpt-4.1")

model = Model(
    api_key="TODO: set your OpenAI API key",
    model=ChatWeaverModelNames.gpt_4_1,
)
```

To remove a custom or existing model name, use `delete()`:

```python
ChatWeaverModelNames.delete("gpt-4.1")
```

#### Important notes

* Adding a model name only makes the string acceptable to ChatWeaver.
* It does not guarantee that your OpenAI account can use that model.
* It does not make non-OpenAI providers compatible with the OpenAI client.
* If the model string is accepted by ChatWeaver but rejected by OpenAI, the error will come from the OpenAI request.

### `ChatWeaverSystemRules`

`ChatWeaverSystemRules` builds reusable system-prompt strings.

It helps keep bot behavior consistent without rewriting long instruction blocks each time. The returned value is a plain string that can be passed to `Bot(rules=...)`.

Available rule presets include:

* `default()`
* `formal_chat()`
* `informal_chat()`
* `formal_email()`
* `informal_email()`

Each preset can be combined with optional formatting and language instructions.

```python
from chatweaver import ChatWeaverSystemRules, Formatting, Language

rules = ChatWeaverSystemRules.default(
    formatting=Formatting.markdown,
    language=Language.EN,
)

bot = Bot(model=model, rules=rules, name="Docs Assistant")
```

#### Formatting presets

`Formatting` contains reusable output-format instructions, such as:

* `Formatting.plain_text`
* `Formatting.plain_text_compact`
* `Formatting.plain_text_wrapped_80`
* `Formatting.key_value_text`
* `Formatting.question_answer_text`
* `Formatting.markdown`
* `Formatting.json`
* `Formatting.yaml`
* `Formatting.unified_diff`
* `Formatting.technical_specification`

Use `formatting=None` when you do not want to append a formatting section.

```python
rules = ChatWeaverSystemRules.default(formatting=None, language=Language.conversation_mirroring)
```

#### Language presets

`Language` contains:

* `Language.conversation_mirroring`, which makes the assistant mirror the user’s language
* Fixed language presets, such as `Language.EN`, `Language.IT`, `Language.FR`, `Language.ES`, and many others

By default, `ChatWeaverSystemRules` uses `Language.conversation_mirroring`.

```python
rules_it = ChatWeaverSystemRules.default(language=Language.IT)
rules_auto = ChatWeaverSystemRules.default(language=Language.conversation_mirroring)
```

#### How rules are used by `Bot`

When a bot generates a completion, `Bot` builds a system message from:

* The bot name
* The selected rules
* The current user name

This means `Bot(name="Support Bot", rules=...)` automatically includes the assistant identity in the system prompt, while `completion(..., user="Diego")` includes the user name for that request.

## Freeze / thaw snapshots

Most core objects can be frozen into serializable dictionaries and restored later.

```python
from chatweaver import Model, Bot, Chat

model = Model(api_key="TODO: set your OpenAI API key")
bot = Bot(model=model)
chat = Chat(bot=bot)

snapshot = chat.freeze(include_secrets=False)
restored = Chat.thaw(snapshot, api_key="TODO: set your OpenAI API key")
```

By default, secrets are excluded:

```python
snapshot = model.freeze(include_secrets=False)  # no API key stored
```

Only use `include_secrets=True` when you explicitly want to store secrets and understand the security implications.

## Troubleshooting / FAQ

1. **How do I get the longest possible response?**

Configure the bot with `max_completion_tokens=None`, which is already the default. Then write the prompt explicitly, for example: “Write the complete code. Do not abbreviate. Do not use placeholders.” If the response may be cut because of length, enable `auto_continue=True` and set a safe `max_continuations` value.

2. **Does `max_completion_tokens=None` mean infinite output?**

No. It means ChatWeaver does not impose an output cap. The model and API still have their own limits.

3. **Why did the answer stop before finishing?**

Check `result.finish_reason`. If it is `"length"`, the model likely hit an output or context limit. Enable `auto_continue=True` or increase `max_continuations`.

4. **Can I use `auto_continue` with `Schema`?**

No. `auto_continue` is intentionally blocked when a structured `response_schema` is used, because multiple continuation calls can break strict JSON validity.

5. **`RuntimeError: Client not available: key_status=<MISSING>...`**

Cause: `Model.api_key` is not set, and the code tries to access `Model.client`.

Fix: Provide a valid API key when constructing `Model`, or set `model.api_key = "..."` before calling remote operations.

6. **`RuntimeError: Client not available: key_status=<INVALID>... Invalid API key format.`**

Cause: API key does not pass the library’s basic format check.

Fix: Set a properly formatted key before calling remote operations.

7. **`ValueError: <Invalid file source (URL not supported): ...>`**

Cause: `file_data` was passed as a URL string.

Fix: Use a local file path, an existing file ID, or an OpenAI `FileObject`.

8. **`ValueError: <Invalid image path or url: ...>`**

Cause: `img_data` is neither a valid URL nor an existing local path.

Fix: Provide a valid URL or a local file path that exists.

9. **`TypeError: <img_data must be a string, pathlib.Path, or list of strings/paths>`**

Cause: `img_data` is a wrong type.

Fix: Pass `str`, `pathlib.Path`, a list of those, or `None`.

10. **`TypeError: <file_data must be a string, pathlib.Path, FileObject, or list of them>`**

Cause: `file_data` is a wrong type.

Fix: Pass a local path, an OpenAI `FileObject`, a file ID string, a list of those, or `None`.

11. **`ValueError: <Invalid 'time_format': expected a valid strftime format>`**

Cause: `Bot.time_format` or `Chat.time_format` was set to an invalid `strftime` format string.

Fix: Use a valid `time.strftime` format, such as `"%d/%m/%Y %H:%M:%S"`.

12. **`ValueError: <Invalid 'creation_date': expected format '%d/%m/%Y %H:%M:%S'>`**

Cause: `Chat.creation_date` does not match the configured `Chat.time_format`.

Fix: Ensure `creation_date` matches `time_format`, or omit it to auto-generate.

13. **Archive load error: `<Invalid cwarchive: bad magic>` or `<Unsupported cwarchive version: ...>`**

Cause: The archive file is not a valid `.cwarchive` file or uses an unsupported version.

Fix: Ensure you saved the archive using `Archive.save()` from a compatible version of `chatweaver`.

14. **Archive load error: `<Corrupted payload (id=...): checksum mismatch>`**

Cause: Archive file corruption or incomplete writes.

Fix: Restore from a backup. `Archive.save()` writes atomically using a temporary file and `os.replace()`, so corruption may indicate external modification or storage issues.

## License

MIT

## Credits / Authors / Acknowledgements

Cecchelani Diego
