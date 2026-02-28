# chatweaver

A Python library that simplifies building AI-driven chatbots with OpenAI, offering conversation management, file attachments, and persistent storage in one cohesive package.

## Overview

### What it is

`chatweaver` is a Python library for building chatbots on top of OpenAI, with:

* A `Model` wrapper for OpenAI client access and API key validation
* A `Bot` abstraction for creating chat completions (including optional images and file attachments)
* A `Chat` session that manages conversation history and reply limits
* A `Schema` helper to request structured JSON outputs
* An `Archive` format (`.cwarchive`) for saving/loading `Model`, `Bot`, `Chat`, and `TextNode` objects

### Why it exists / main value

It provides a cohesive set of building blocks to:

* Manage conversations with history
* Attach images and upload files (local paths) to OpenAI
* Persist and restore bots/chats/models (with secrets excluded by default)

### Key features

* Conversation management via `Chat` with message history (`TextNode`) and reply limits
* OpenAI model wrapper with lazy API key validation (`Model`)
* Support for attachments:

  * Images from local paths (embedded as base64 data URLs) or from URLs
  * Files from local paths (uploaded) or file IDs
* Structured outputs via `Schema` (`response_format` JSON schema)
* Persistence to a binary `.cwarchive` file via `Archive` (atomic save + integrity checks)
* Freeze/thaw snapshots for `Model`, `Bot`, `Chat`, `Schema`, and `TextNode`

### Typical use cases

* Build an OpenAI-powered chatbot with a managed conversation history
* Add image inputs (URL or local path) to a prompt
* Upload local files and attach them to the request
* Enforce a rolling chat history using a reply limit
* Save and restore chat sessions/bots/models without storing API keys by default

## Installation

### Requirements

* Python >= 3.10
* OS Independent (per project classifiers)
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

### 2) Request structured output with `Schema`

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

### 3) Attach images (URL or local path)

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

### 4) Attach files (local path upload or file_id)

Files can be:

* A file ID (already uploaded)
* A local path (uploaded via the OpenAI Files API with purpose="user_data")
* URLs are **not supported** for files (will raise `ValueError`)

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

* `api_key` is not validated on set. It is validated when `client` is accessed (lazy validation).
* If the API key format is invalid (does not start with `"sk-"` or is too short), `key_status` becomes `INVALID` and `last_auth_error` is set to `"Invalid API key format."`.
* Accessing `client` when the key cannot be validated raises `RuntimeError` with the reason.

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
    ) -> "BotCompletionResult": ...
```

#### Parameters

* `prompt`: The user prompt string.
* `user`: Name of the user (included in the system prompt).
* `history`: Optional message list prepended to the constructed system/user messages. In `Chat`, this is built from `TextNode` entries via `dict(node)`.
* `img_data`:

  * `str`/`pathlib.Path`: a single image URL or local path
  * `list[str|pathlib.Path]`: multiple image URLs/paths
  * Local paths are base64-encoded into a `data:image/png;base64,...` URL.
* `file_data`:

  * `str`/`pathlib.Path`: a local path (uploaded) or a file ID string
  * `FileObject`: OpenAI file object (treated as a file ID)
  * `list[...]`: multiple local paths / file IDs / `FileObject`s
  * URLs are **not supported** for files.
* `response_schema`: A `Schema` to use for this request. If omitted, `Bot.schema` is used.

#### Returns

* `BotCompletionResult` containing:

  * `content` (assistant message content or refusal)
  * token usage (`prompt_tokens`, `completion_tokens`, `total_tokens`)
  * timestamps (`start_date`, `final_date`) and timing (`delta_time`)
  * input/output metadata (`MetadataContainer`)

#### Raised exceptions (selected)

* `TypeError` if `img_data`, `file_data`, or `response_schema` types are invalid
* `ValueError` if an image path/URL is invalid, or if `file_data` is a URL (unsupported)
* `RuntimeError` from `Model.client` if remote services are not available due to missing/invalid key
* Other exceptions may bubble up from the OpenAI client

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

* `replies_limit=None` means no limit (internally `float("inf")`).
* `history` accepts:

  * `list[TextNode]`
  * `list[dict]` (either frozen snapshots or plain dict payloads)
* `response()` appends a user `TextNode` and an assistant `TextNode` to history (dropping oldest pairs when at limit).

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
* `retrieve(..., api_key=..., api_key_provider=...)` can inject API keys during restoration (keys are not stored unless saved with `include_secrets=True`).
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

### Models

`ChatWeaverModelNames` provides predefined model name strings and allows controlled extension:

* Built-in fields include:

  * `"gpt-4"`, `"gpt-4o"`, `"gpt-4-turbo"`, `"o1"`, `"o1-mini"`, `"o3"`

```python
from chatweaver import ChatWeaverModelNames

print(ChatWeaverModelNames.gpt_4o)
print(ChatWeaverModelNames.get_all_models())

ChatWeaverModelNames.add("claude-3-opus")   # adds a new model name (if valid)
ChatWeaverModelNames.delete("claude-3-opus")  # deletes it (if present)
```

### System rules, formatting, language

`ChatWeaverSystemRules` returns predefined instruction strings for system prompts, optionally augmented with:

* `Formatting` enum presets (e.g., `Formatting.plain_text`, `Formatting.markdown`, etc.)
* `Language` enum presets (e.g., `Language.conversation_mirroring`, `Language.EN`, etc.)

```python
from chatweaver import ChatWeaverSystemRules, Formatting, Language

rules = ChatWeaverSystemRules.default(formatting=Formatting.markdown, language=Language.EN)
```

## Troubleshooting / FAQ

1. **`RuntimeError: Client not available: key_status=<MISSING>...`**

* Cause: `Model.api_key` is not set, and the code tries to access `Model.client` (e.g., during `Bot.completion()` or file uploads).
* Fix: Provide a valid API key when constructing `Model`, or set `model.api_key = "..."` before calling remote operations.

2. **`RuntimeError: Client not available: key_status=<INVALID>... Invalid API key format.`**

* Cause: API key does not start with `"sk-"` or is too short.
* Fix: Set a properly formatted key (must start with `"sk-"` and be length >= 20, per the library’s format check).

3. **`ValueError: <Invalid file source (URL not supported): ...>`**

* Cause: `file_data` was passed as a URL string.
* Fix: Use a local file path (it will be uploaded) or pass an existing file ID.

4. **`ValueError: <Invalid image path or url: ...>`**

* Cause: `img_data` is neither a valid URL nor an existing local path.
* Fix: Provide a valid URL (`scheme` + `netloc`) or a local file path that exists.

5. **`TypeError: <img_data must be a string, pathlib.Path, or list of strings/paths>`**

* Cause: `img_data` is a wrong type (e.g., dict or bytes).
* Fix: Pass `str`, `pathlib.Path`, a list of those, or `None`.

6. **`TypeError: <file_data must be a string, pathlib.Path, FileObject, or list of them>`**

* Cause: `file_data` is a wrong type.
* Fix: Pass a local path (`str`/`pathlib.Path`), an OpenAI `FileObject`, a file ID string, a list of those, or `None`.

7. **`ValueError: <Invalid 'time_format': expected a valid strftime format>`**

* Cause: `Bot.time_format` or `Chat.time_format` was set to an invalid `strftime` format string.
* Fix: Use a valid `time.strftime` format, such as `"%d/%m/%Y %H:%M:%S"`.

8. **`ValueError: <Invalid 'creation_date': expected format '%d/%m/%Y %H:%M:%S'>`**

* Cause: `Chat.creation_date` does not match the configured `Chat.time_format`.
* Fix: Ensure `creation_date` matches `time_format`, or omit it to auto-generate.

9. **Archive load error: `<Invalid cwarchive: bad magic>` or `<Unsupported cwarchive version: ...>`**

* Cause: The archive file is not a valid `.cwarchive` file or uses an unsupported version.
* Fix: Ensure you saved the archive using `Archive.save()` from a compatible version of `chatweaver`.

10. **Archive load error: `<Corrupted payload (id=...): checksum mismatch>`**

* Cause: Archive file corruption or incomplete writes.
* Fix: Restore from a backup. `Archive.save()` writes atomically using a temporary file and `os.replace()`, so corruption may indicate external modification or storage issues.

## License

MIT

## Credits / Authors / Acknowledgements

Cecchelani Diego