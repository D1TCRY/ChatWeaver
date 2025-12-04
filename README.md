# ChatWeaver – A Comprehensive Overview

**ChatWeaver** is a Python library designed to simplify and enhance chatbot development with OpenAI. By offering intuitive abstractions and structures—such as the `Model`, `Bot`, `Chat`, `TextNode`, and `CWArchive` classes—ChatWeaver consolidates much of the boilerplate and complexity associated with multi-turn conversations, file integrations, and persistent storage.

---

## Why ChatWeaver?

1. **Abstraction Layer**: It wraps the OpenAI API in high-level classes, reducing the need to manage low-level prompts and token usage manually.  
2. **Conversation Management**: Built-in classes handle chat history, user messages, file attachments, and more.  
3. **Persistence**: You can easily save and retrieve entire `Chat` sessions or multiple objects with `CWArchive`.  
4. **Scalability**: Configuration of models, tokens, and asynchronous loading helps you tailor ChatWeaver to your production environment.

---

## Core Components

### 1. `Model`
A wrapper for OpenAI-based models, ensuring valid API keys and model names.

- **Initialization**:
  ```python
  from chatweaver import Model
  
  # Provide an API key and optionally specify the model name
  model = Model(api_key="sk-1234567890abcdef1234...", model="gpt-4o")
  ```

- **Key Capabilities**:
  - Stores and validates the API key and model name.
  - Initializes the internal OpenAI client automatically.
  - Provides getters and setters for dynamic updates to the model or API key.

### 2. `Bot`
Extends `Model` to create a customizable AI assistant with definable rules and a unique name.

- **Initialization**:
  ```python
  from chatweaver import Bot
  
  bot = Bot(
      api_key="sk-1234567890abcdef1234...",
      rules="You are a helpful assistant that responds concisely.",
      name="ConciseBot"
  )
  ```

- **Key Capabilities**:
  - Holds conversation rules and styling (e.g., formal, casual, JSON output).
  - Offers a `response(...)` method to generate replies to user prompts, including support for file attachments.

### 3. `TextNode`
A lightweight, immutable container for individual messages in a conversation.

- **Example**:
  ```python
  from chatweaver import TextNode
  
  # Represents a user's message
  user_node = TextNode(
      role="user",
      content="Hello, what's the weather like?",
      owner="Alice",
      tokens=8,
      date="2025-01-01 09:15:00"
  )
  ```
  
- **Key Capabilities**:
  - Stores message details like role (assistant/user), content, tokens used, and timestamp.
  - Easily converted to a dictionary or a string for logging or serialization.

### 4. `Chat`
Builds upon the `Bot` to manage an entire conversation session, storing user/assistant exchanges (`TextNode` objects), reply limits, and session-level metadata like title or creation date.

- **Initialization**:
  ```python
  from chatweaver import Chat

  # Pass an existing Bot or let Chat create its own under the hood
  chat_session = Chat(
      api_key="sk-1234567890abcdef1234...",
      title="Support Session",
      replies_limit=5,
      user="Customer"
  )
  ```
  
- **Key Capabilities**:
  - Maintains a list of messages in `chat_history`.
  - Applies a maximum reply count (`chat_replies_limit`).
  - Offers `get_response(...)` to seamlessly generate and store new user and assistant messages:
    ```python
    user_input = "Hi! I need help with my order."
    assistant_reply = chat_session.get_response(prompt=user_input)
    print("Assistant:", assistant_reply)
    ```

- **Useful Properties**:  
  - `chat_replies` – counts how many user+assistant pairs have occurred.  
  - `chat_cost` – sums the tokens used across all messages.  
  - `chat_title` – a helpful descriptor for logs or archives.  

### 5. `CWArchive`
Handles persistent storage of any combination of `Chat`, `Bot`, or `Model` objects. You can load, save, and manage them by their integer IDs or by direct reference to the objects.

- **Initialization**:
  ```python
  from chatweaver import CWArchive
  
  archive = CWArchive(
      path="my_chats.archive"
  )
  ```
  
- **Key Capabilities**:
  - **Add/Remove**: Insert or delete items (by ID or by object).  
  - **Retrieve**: Load all items from disk, either sequentially or concurrently. (better using the archive_data attribute instead) 
  - **Save**: Write the current in-memory items back to the file, ensuring data consistency.  

- **Usage**:
  ```python
  # Suppose we have a Chat object we want to store
  chat_session = Chat(api_key="sk-1234567890abcdef1234...", title="My Chat Session")
  
  # Add the chat to the archive
  archive.add(chat_session)
  
  # Save changes to disk
  archive.save()
  
  # Retrieve all objects (may load asynchronously in parallel)
  data = archive.archive_data
  for item_id, chat_obj in data.items():
      print(item_id, chat_obj)
  
  # Remove an item (by ID or by reference)
  archive.remove(0)      # remove the object with ID = 0
  # or
  archive.remove(chat_session)
  ```

---

## Putting It All Together – Example Workflow

Below is a high-level example illustrating how you might use **ChatWeaver** end-to-end:

```python
from chatweaver import Model, Bot, Chat, CWArchive

# 1. Create a Model
model = Model(api_key="sk-1234567890abcdef1234", model="gpt-4o")

# 2. Create a Bot with custom rules, tied to the Model
rules = "You are a friendly and knowledgeable assistant."
bot = Bot(
    cw_model=model,
    rules=rules,
    name="HelpfulBot"
)

# 3. Start a Chat session using the Bot
chat = Chat(
    cw_bot=bot,
    title="Demo Session",
    replies_limit=3,  # limit to 3 user+assistant replies
    user="Tester"
)

# 4. Interact with the Chat
response1 = chat.get_response("Hello, how are you?")
print("Bot:", response1)

response2 = chat.get_response("Can you tell me a joke?")
print("Bot:", response2)

# Check Chat details
print("Current replies used:", chat.chat_replies)
print("Total tokens so far:", chat.chat_cost)

# 5. Save the Chat to an Archive
archive = CWArchive(path="demo_archive.txt", asynchronous=True, delay=0.07)
archive.add(chat)
archive.save()

# 6. Retrieve data from the archive and display
loaded_data = archive.archive_data
for item_id, obj in loaded_data.items():
    print(f"Item ID {item_id} -> {obj}")
```

In this script:

1. **Model**: We create or reference an OpenAI model with a valid API key.  
2. **Bot**: We attach conversation rules and specify a bot name, letting it use our `Model`.  
3. **Chat**: We start a conversation session, linking it to our `Bot`. We optionally limit how many user+assistant pairs are allowed.  
4. **Conversation**: We ask the bot questions and observe the replies.  
5. **Persistence**: Finally, we save the entire `Chat` to an archive file and later re-load it to continue the session.

---

## Final Thoughts

**ChatWeaver** aims to reduce the friction in creating robust, multi-turn chatbot experiences powered by OpenAI. Whether you need to store your sessions locally, manage advanced conversation rules, or simply test a new idea in minutes, ChatWeaver’s structured approach and flexible design provide a powerful toolkit for modern chatbot development.

---

# ChatWeaver – A Detailed Overview

---

## Model

The **Model** class provides a straightforward way to configure and manage OpenAI-based API clients. It validates and stores both the model name and the API key, automatically initializing a matching OpenAI client for you.  

---

### Description

- **Purpose**: Encapsulate the details of model configuration (e.g., the model name, API key, and associated client) to simplify usage within your application.
- **Validation**: Ensures both the API key and model name meet the required formats and are tested before actual usage.
- **Automatic Client Creation**: Whenever you update the API key, a new OpenAI client is initialized if validation succeeds.

---

### Attributes

- **`model_api_key: str`**  
    Retrieve or set the API key associated with this Model. Must begin with `"sk-"` and be at least 20 characters long.
  
- **`model_model: str`**  
    Retrieve or set the model name. The default value is `"gpt-4o"`. Changing this property triggers internal validation against an accepted list of models.

- **`model_client: openai.OpenAI`**  
    Retrieve the current OpenAI client. When the API key changes, a new client is automatically created.

---

### Methods

Below is an overview of the principal methods available on the **Model** class.  

- **Constructor**  
    **`__init__(api_key: str, model: str = "gpt-4o")`**  
    Initializes the **Model** with a valid API key and an optional model name.  
    - **Parameters**:  
        - `api_key (str)`: Must begin with `"sk-"` and be at least 20 characters.  
        - `model (str)`: The model name to use, defaulting to `"gpt-4o"`.  
    - **Raises**:  
        - `Exception`: If either the model name or the API key fails validation.

- **`__str__() -> str`**  
    Returns a user-friendly string containing the current model name and a partially obfuscated API key.

- **`__repr__() -> str`**  
    Returns a more detailed string representation useful for debugging or logging.

- **`__eq__(other) -> bool`**  
    Determines equality between two **Model** instances by comparing both their model names and API keys.

- **`model_model (getter)`**  
    Retrieves the currently set model name.

- **`model_model (setter)`**  
    Validates and sets a new model name. Raises an `Exception` if the new name is not in the accepted list of models.

- **`model_api_key (getter)`**  
    Retrieves the currently stored API key.

- **`model_api_key (setter)`**  
    Validates the format of the new API key (must start with `"sk-"` and be at least 20 characters). Performs a test request to ensure the key is valid. If successful, updates the API key and re-initializes the client.

- **`model_client (getter)`**  
    Retrieves the OpenAI client currently in use.

- **`model_client (setter)`**  
    Explicitly sets a new OpenAI client by providing the same API key already stored in `model_api_key`. If the provided key does not match the stored one, an exception is raised.

---

### Usage Example

```python
from chatweaver import Model

# Initialize the Model with a valid API key and optionally specify the model name
model_instance = Model(api_key="sk-1234567890abcdef1234", model="gpt-4o")

# Check basic info
print(str(model_instance))  
# Example Output: <Model | model=gpt-4o, api_key=sk-1234567...4564>

# Update the model name (must be in the allowed set of models)
model_instance.model_model = "gpt-4o"

# Update the API key (re-initializes the OpenAI client if validation succeeds)
model_instance.model_api_key = "sk-0987654321abcdef5678"

# Retrieve the OpenAI client to make requests manually (if needed)
client = model_instance.model_client

# Compare with another Model instance
another_model = Model(api_key="sk-0987654321abcdef5678", model="gpt-4o")
print(model_instance == another_model)  # True, if both model name and API key match
```

Use the **Model** class to simplify how you manage different OpenAI models and keys across your chatbot applications.

---
---
## Bot

The **Bot** class extends the capabilities of the `Model` class to create a conversational AI entity. It allows you to specify custom rules, assign a name to the bot, and configure time formats. You can also use it to generate responses to user queries, optionally integrating images or file uploads.  

---

### Description

- **Purpose**: Provide a flexible chatbot built on a specific `Model`.  
- **Customization**: Lets you define conversation rules, set a bot name, and attach images or files to user prompts.  
- **Integration**: If you already have a `Model` instance, you can pass it in; otherwise, the `Bot` will initialize its own `Model` by inheriting from `Model`.  

---

### Attributes

- **`bot_rules: str`**  
  The conversation rules that guide the bot’s responses. These rules can be overridden if needed. The getter automatically appends the bot’s name to provide context in dialogues.

- **`bot_name: str`**  
  The human-readable name assigned to the bot (default is `"AI Bot"`). This name also appears in the conversation rules.

- **`bot_time_format: str`**  
  The format string used for handling timestamps in the bot’s operation (default is `"%d/%m/%Y %H:%M:%S"`).

- **`bot_Model: Model`**  
  The underlying `Model` instance that interfaces with OpenAI. Access this property when you need direct control over the model settings or the OpenAI client.

---

### Methods

Below is a summary of the key methods in the **Bot** class.

#### Constructor

**`__init__( *args, rules: str | None = ..., name: str = "AI Bot", cw_model: Model | None = None, **kwargs ) -> None`**  

Initializes the **Bot** with optional rules, a custom name, and an existing `Model` (if available). If no `Model` is provided, the bot internally creates one by calling `super().__init__`.

- **Parameters**:  
  - `*args`: Additional positional arguments passed to the parent `Model` if `cw_model` is not given.  
  - `rules (str | None)`: Conversation rules for the bot. Falls back to default if `None`.  
  - `name (str)`: The bot’s name (default is `"AI Bot"`).  
  - `cw_model (Model | None)`: An existing `Model` instance. If `None`, a new `Model` is created.  
  - `**kwargs`: Additional keyword arguments passed to the parent `Model` if `cw_model` is not given.  

- **Raises**:  
  - `TypeError`: If `cw_model` is provided but is not a `Model` instance.

---

#### `__str__() -> str` 
Returns a friendly string with the bot’s name, for quick identification.

#### `__repr__() -> str`  
Returns a more detailed string representation, useful for debugging (includes name, rules, and the underlying `Model`).

#### `__eq__(other: Bot) -> bool`  
Compares this bot to another **Bot** instance. Returns `True` if both have the same rules, name, and underlying `Model`.

---

#### `bot_Model (getter)`
Retrieves the underlying `Model` used by this bot. This allows you to work directly with the `Model`’s methods and properties if needed.

#### `bot_rules (getter/setter)`  
- **Getter**: Returns the bot’s current rules (automatically appending the bot’s name).  
- **Setter**: Updates the bot’s rules. If `None`, defaults to a predefined rule set.  

#### `bot_name (getter/setter)`  
- **Getter**: Returns the bot’s current name.  
- **Setter**: Assigns a new name to the bot, which also appears in its rules.  

#### `bot_time_format (getter/setter)`  
- **Getter**: Returns the bot’s time format string.  
- **Setter**: Assigns a new time format. Raises a `ValueError` if the format is invalid.

---

### Generating Responses

Use the **`response`** method to get a chatbot response from a user prompt:

**`response(prompt: str, user: str = "User", history: list | None = None, image_path: str | None = None, file_path: str | None = None) -> dict[str, Any]`**  

Constructs a message set (including optional conversation history) and sends it to the underlying `Model`’s OpenAI client. If `image_path` or `file_path` is provided, these files are appropriately handled (e.g., base64-encoded images, file uploads) and referenced in the prompt.

- **Parameters**:  
  - `prompt (str)`: The user’s query or statement.  
  - `user (str)`: A label for the user in conversation (default is `"User"`).  
  - `history (list | None)`: Optional prior messages to maintain context.  
  - `image_path (str | None)`: Local path to an image to be included.  
  - `file_path (str | None)`: Local path to any file to upload and reference.  

- **Returns** (`dict[str, Any]`):  
  - `"content"`: The text generated by the model.  
  - `"prompt_tokens"`, `"completion_tokens"`, `"total_tokens"`: Token usage statistics.  
  - `"start_date"`: Timestamp at which the request started.  
  - `"final_date"`: Timestamp at which the request finished.  
  - `"delta_time"`: Elapsed time for the model to produce the response.

---

### Usage Example

```python
from chatweaver import Bot, Model

# 1. Using an existing Model
existing_model = Model(api_key="sk-1234567890abcdef1234...", model="gpt-4o")
bot = Bot(
    cw_model=existing_model,
    rules="You are a helpful assistant with a witty sense of humor.",
    name="FriendlyBot"
)

# 2. Or let Bot create a new Model internally
another_bot = Bot(
    api_key="sk-0987654321abcdef5678...",   # Passed to Model's constructor
    rules="You are a formal assistant that provides concise answers.",
    name="ConciseBot"
)

# 3. Generating a response to a user prompt
response_data = bot.response(
    prompt="What is the capital of France?",
    user="Alice",
    image_path=None,
    file_path=None
)

# Check response
print("Bot response:", response_data["content"])
print("Token usage:", response_data["total_tokens"])
```

In this example, you can see how you might create `Bot` instances—either using an existing `Model` or letting `Bot` handle model creation. You can then generate answers to user prompts, optionally providing conversation history and file attachments.

---
---

## TextNode

The **TextNode** class is a simple, immutable data container representing a single message in a conversation. Each instance stores key information about the message, including its role (assistant or user), the message content, the name of the owner, token usage, and creation date.

---

### Description

- **Immutability**: `TextNode` is defined with `@dataclass(frozen=True)`, meaning its fields cannot be modified after creation.  
- **Conversation Element**: Each `TextNode` encapsulates one message. In a broader chatbot flow, multiple `TextNode` instances together form the conversation history.

---

### Attributes

- **`role: str`**  
  The role associated with this text node, typically `"assistant"` or `"user"`.

- **`content: str`**  
  The actual text content of the message.

- **`owner: str`**  
  The name or identifier of the owner of this node (e.g., `"AI Bot"`, `"User"`, etc.).

- **`tokens: int`**  
  The number of tokens estimated or measured for this message content. Useful for tracking token usage in OpenAI-based systems.

- **`date: str`**  
  A string representation of the date or timestamp at which this message was created.

---

### Methods

- **`__str__() -> str`**  
  Returns a JSON-like string of all attributes in the `TextNode`. For example:

  ```python
  {
      "role": "assistant",
      "content": "Hello!",
      "owner": "AI Bot",
      "tokens": 5,
      "date": "2024-12-31 10:00:00"
  }
  ```

- **`__iter__() -> dict`**  
  Provides an iterator over the `TextNode`’s attributes as key-value pairs. This allows you to quickly convert a `TextNode` to a dictionary by calling `dict(text_node_instance)`.

---

### Usage Example

Below is a simple demonstration of how you might create a `TextNode` and then inspect its attributes.

```python
from chatweaver import TextNode

# Create a TextNode representing a user's message
user_message = TextNode(
    role="user",
    content="What's the weather like today?",
    owner="Alice",
    tokens=8,
    date="2025-01-01 09:15:00"
)

# Print the node in a JSON-like string representation
print(str(user_message))
# Output:
# {
#   'role': 'user', 
#   'content': "What's the weather like today?", 
#   'owner': 'Alice', 
#   'tokens': 8, 
#   'date': '2025-01-01 09:15:00'
# }

# Convert the TextNode to a dictionary for further processing
node_dict = dict(user_message)
print(node_dict["content"])  # "What's the weather like today?"
```

Use `TextNode` objects to store and pass around conversation messages reliably, ensuring their metadata remains intact across different parts of your chatbot or application.

---
---

## Chat

The **Chat** class extends the functionality of the `Bot` class to manage a full conversation session. It retains a history of messages (via `TextNode` objects), handles reply limits, and tracks metadata such as the chat title, creation date, and total cost (in tokens). This class is ideal for organizing multi-turn conversations in applications or services that require persistent context.

---

### Description

- **Purpose**: Provide a structured environment for handling multiple user-bot interactions within one session.  
- **Key Features**:  
  - Maintains an ordered conversation history as a list of `TextNode`s.  
  - Tracks and enforces a maximum number of user+assistant reply pairs.  
  - Allows attachments (images/files) to be provided in prompts.  
  - Integrates seamlessly with a `Bot` (and thus with a `Model`) to generate responses.  
- **Metadata**: Stores creation date, title, and calculates token-based costs from the conversation history.

---

### Attributes

- **`chat_time_format: str`**  
  The string format used for timestamps (by default `"%d/%m/%Y %H:%M:%S"`).

- **`chat_replies_limit: int`**  
  The maximum number of user+assistant reply pairs allowed in the session. If set to `None`, there is no limit.

- **`chat_history: list[TextNode]`**  
  A list of `TextNode` instances, each representing a message (user or assistant) in the conversation.

- **`chat_user: str`**  
  The identifier for the user participating in the chat (e.g., `"User"`, `"Alice"`, etc.).

- **`chat_creation_date: str`**  
  A timestamp indicating when the chat session was created, using `chat_time_format`.

- **`chat_replies: int`**  
  The current number of user+assistant message pairs in the conversation (computed from `chat_history`).

- **`chat_cost: int`**  
  The sum of all tokens used across the conversation. Calculated by summing the `tokens` attribute of each `TextNode`.

- **`chat_title: str`**  
  A descriptive title for the chat session (e.g., `"New Chat"`, `"Customer Support Session"`, etc.).

---

### Methods

#### Constructor

**`__init__(*args, title="New Chat", replies_limit=10, user="User", cw_bot=None, **kwargs)`**  
Creates a new chat session with an optional title, reply limit, user identifier, and existing `Bot`. If no `Bot` is provided, the constructor creates one internally (inheriting from `Bot`).

- **Parameters**:  
  - `*args`: Positional arguments passed to the underlying `Bot` or `Model` constructor, if `cw_bot` is not provided.  
  - `title (str)`: The chat title (`"New Chat"` by default).  
  - `replies_limit (int | None)`: The maximum number of user+assistant pairs. `None` means no limit (defaults to `10`).  
  - `user (str)`: Name or identifier of the user (`"User"` by default).  
  - `cw_bot (Bot | None)`: An existing `Bot`. If `None`, a new one is created.  
  - `**kwargs`: Additional keyword arguments passed to the `Bot` or `Model` constructor if `cw_bot` is not provided.

- **Raises**:
  - `TypeError`: If `cw_bot` is provided but is not a `Bot` instance.

---

#### `__str__() -> str`  
Returns a concise string representation, including the chat title, reply limit, current reply count, and creation date.

#### `__repr__() -> str`  
Returns a detailed string for debugging or logging, including attributes such as the reply limit, user, title, and the associated `Bot`.

#### `__lt__(other: Chat) -> bool`  
Enables chronological sorting by comparing `chat_creation_date` between two `Chat` instances.

#### `__eq__(other: Chat) -> bool`  
Checks if two `Chat` objects have the same essential attributes: reply limit, user, title, creation date, number of replies, history, and the same underlying `Bot`.

---

#### Properties

- **`chat_Bot (getter)`**  
  Retrieves the underlying `Bot` instance. Useful if you need direct access to its rules or the `Model` it uses.

- **`chat_time_format (getter/setter)`**  
  - **Getter**: Returns the time format string for timestamps.  
  - **Setter**: Validates a new time format by attempting to format the current time. Raises a `ValueError` if invalid.

- **`chat_replies_limit (getter/setter)`**  
  - **Getter**: Returns the maximum allowed replies (`float('inf')` if no limit).  
  - **Setter**: Accepts an integer or `None` (treated as infinite). Raises a `TypeError` if the value cannot be converted to `int`.

- **`chat_history (getter/setter)`**  
  - **Getter**: Returns a list of the conversation’s `TextNode` messages.  
  - **Setter**: Accepts a list of `TextNode`s or a list of dictionaries convertible to `TextNode`. Raises a `TypeError` for invalid data.

- **`chat_user (getter/setter)`**  
  - **Getter**: Returns the user’s name or identifier.  
  - **Setter**: Assigns a new user identifier as a `str`.

- **`chat_creation_date (getter/setter)`**  
  - **Getter**: Returns the creation date as a `str` formatted according to `chat_time_format`.  
  - **Setter**: Validates that the given string matches the current time format; raises `ValueError` if incorrect.

- **`chat_replies (getter)`**  
  Calculates the number of user+assistant pairs from the `chat_history`. Each pair corresponds to two messages (one user and one assistant).

- **`chat_cost (getter)`**  
  Sums the `tokens` attribute of each `TextNode` in `chat_history` to provide a cumulative token usage.

- **`chat_title (getter/setter)`**  
  - **Getter**: Retrieves the session’s title.  
  - **Setter**: Assigns a new session title as a `str`.

---

#### `set_all(return_self: bool = True, **kwargs: Any) -> Chat | None`  
Dynamically updates multiple attributes on the `Chat` (and on its underlying `Bot` or `Model`) using keyword arguments.  
- **Usage**: Each key should refer to the private attribute path (e.g., `"_Chat__user"`, `"_Bot__rules"`, `"_Model__api_key"`).  
- **Returns**: The `Chat` instance itself if `return_self` is `True`, otherwise `None`.

---

### Generating Responses

Use **`get_response`** to interact with the chat:

**`get_response(prompt: str, user: str | None = None, image_path: str | None = None, file_path: str | None = None) -> str`**  

Generates an assistant’s response to the given `prompt`, optionally attaching an image or file. The new user and assistant messages are appended to `chat_history` as `TextNode` objects.

- **Parameters**:  
  - `prompt (str)`: The user’s text input.  
  - `user (str | None)`: Custom user identifier for this prompt. Defaults to `chat_user` if `None`.  
  - `image_path (str | None)`: Path to an image file to include in the request.  
  - `file_path (str | None)`: Path to a file to upload for reference.  

- **Returns**:  
  - A `str` containing the assistant’s response content.

---

### Example Usage

```python
from chatweaver import Chat, Bot, TextNode

# 1. Creating a Chat with a custom Bot
my_bot = Bot(api_key="sk-1234567890abcdef1234...", rules="You are a friendly assistant.")
my_chat = Chat(
    cw_bot=my_bot,
    title="My AI Discussion",
    replies_limit=5,
    user="Alice"
)

# 2. Getting a response
assistant_reply = my_chat.get_response("Hello, can you tell me a joke?")
print("Assistant says:", assistant_reply)

# 3. Accessing chat history
for node in my_chat.chat_history:
    print(node.role, node.content, sep=": ")

# 4. Viewing total token usage
print("Total token usage:", my_chat.chat_cost)

# 5. Changing chat title
my_chat.chat_title = "Jokes and More"

# 6. Setting multiple attributes at once
my_chat.set_all(
    _Chat__replies_limit=None,   # No longer limit the replies
    _Bot__rules="Stay professional in your answers."
)

print("Updated chat limit:", my_chat.chat_replies_limit)
print("Updated bot rules:", my_chat.chat_Bot.bot_rules)
```

In this example, you create a `Chat` using a specific `Bot`, ask for a response, and then manipulate or inspect the `Chat`’s properties. The session automatically tracks message history (via `TextNode` objects), token usage, and enforces reply limits (if specified).

---
---

## CWArchive

The **CWArchive** class provides a convenient way to store and manage `Chat`, `Bot`, or `Model` objects in a single file. It supports both synchronous and asynchronous loading, as well as basic add, remove, and retrieval operations. This makes it suitable for saving and restoring chatbot sessions, bots, or model configurations in a controlled, persistent manner.

---

### Description

- **Purpose**: Encapsulate file-based storage of `Chat`, `Bot`, and `Model` objects with minimal setup.  
- **Asynchronous Support**: Can operate in asynchronous mode, splitting the data into chunks and loading them in parallel.  
- **Archive Operations**: Offers methods to add or remove objects (by ID or directly), retrieve the entire archive, and save changes back to disk.  
- **Thread-Safety Caveat**: Running operations asynchronously in certain environments can lead to race conditions. If this happens, the delay or asynchronous behavior can be tweaked to mitigate the issue.
- Context Manager: The `__enter__` and `__exit__` methods handle setup and teardown logic, ensuring that save() is automatically called on exit.

---

### Attributes

- **`archive_path: str`**  
  The filesystem path where the archive is stored.

- **`archive_data: dict`**  
  A dictionary of stored objects, keyed by integer IDs.

- **`archive_id: int`**  
  The next available integer ID that can be used when adding a new item.

- **`archive_delay: float`**  
  The delay (in seconds) between asynchronous load operations. Adjust this if you experience race conditions in multi-threaded contexts.

- **`archive_asynchronous: bool`**  
  Controls whether the archive is loaded/saved asynchronously. If set to `False`, data loading is done sequentially.

---

### Methods

Below is an overview of the most important methods in **CWArchive**.

#### Constructor

**`__init__(path: str, asynchronous: bool = True, delay: float = 0.07)`**  
Initializes a new archive with the specified file path, async flag, and an optional delay for asynchronous loads.

- **Parameters**:  
  - `path (str)`: The path to the archive file on disk.  
  - `asynchronous (bool)`: Determines if loading is handled asynchronously (`True` by default).  
  - `delay (float)`: Time in seconds to wait between asynchronous load operations. Defaults to `0.07`.  

- **Raises**:  
  - `TypeError`: If `asynchronous` is not a boolean.

- **Potential Race Condition**:  
  If the asynchronous loading processes attempt to modify shared data at the same time, errors can occur. Consider increasing `delay` or setting `archive_asynchronous` to `False`.

---

#### `__str__() -> str`  
Returns a user-friendly string with the path of the archive, e.g., `"<Archive | path=/path/to/archive>"`.

#### `__repr__() -> str`  
Returns a formal string representation of the archive for debugging purposes, e.g., `"Archive(path='...')"`.  

#### `__len__() -> int`  
Returns the count of items (key-value pairs) currently in the archive.

#### `__add__(other: Chat | Bot | Model)`  
Enables using the `+` operator to add a `Chat`, `Bot`, or `Model` object to the archive.  
```python
my_archive = CWArchive("chats.archive")
my_archive + my_chat  # Adds 'my_chat' under the next available ID
```

#### `__sub__(other: int | Chat | Bot | Model)`  
Enables using the `-` operator to remove an element from the archive by its integer ID or by an instance of `Chat`, `Bot`, or `Model`.  
```python
my_archive - 0         # Removes the item with ID 0
my_archive - my_chat   # Removes the specific Chat instance
```

#### `__enter__(self, *args, **kwargs) -> CWArchive`
Returns the `CWArchive` instance upon entering a with block, allowing you to perform archive operations within that scope.
```python
with CWArchive(path="my_archive.txt") as archive:
    ...
```

#### `__exit__(self, *args, **kwargs) -> None`
Called automatically upon exiting the with block. By default, it invokes save(), ensuring that any modifications made to the archive during the block are persisted to disk.
```python
with CWArchive(path="my_archive.txt") as archive:
    # All changes, like adding or removing objects, 
    # will be saved when exiting this block.
```

---

### Core Archive Actions

- **`define(path: str, delay: float) -> None`**  
  Updates the archive file path and the delay for asynchronous operations.

- **`get_id_from_element(element: Chat | Bot | Model) -> list[int]`**  
  Returns a list of all IDs in the archive that correspond to the provided object. Useful if the same object was stored multiple times.

- **`is_valid_id(identifier: int) -> bool`**  
  Checks whether the given ID exists in the archive.

- **`add(element: Chat | Bot | Model) -> None`**  
  Inserts an element (if it is an instance of `Chat`, `Bot`, or `Model`) into the archive under the next available integer ID.  

- **`remove(element: list | set | tuple | int | Chat | Bot | Model, remove_type: str | None = "all") -> None`**  
  Removes one or multiple elements from the archive.  
  - **`element`**: Can be a single ID, a single object, or an iterable of IDs/objects.  
  - **`remove_type`**: Accepts `"all"`, `"first"`, or `"last"` to handle cases where the same object appears more than once.

- **`save() -> None`**  
  Serializes and writes the archive data to disk in sorted order (by the object’s representation).  
  ```python
  my_archive.save()  # Commits changes to file
  ```

- **`retrieve() -> dict[int, Chat | Bot | Model]`**  
  Reads the archive file from disk and converts each item’s string representation into its corresponding object. Supports both synchronous and asynchronous loading.  
  - **Asynchronous**: Splits the data into chunks and loads them concurrently, separated by `archive_delay` seconds.  
  - **Synchronous**: If `archive_asynchronous` is `False`, loads data one item at a time.

---

### Usage Example

```python
from chatweaver import CWArchive, Chat

# 1. Create an archive (asynchronous by default) with a specific file path
archive = CWArchive(path="my_archive.txt")

# 2. Add a new Chat object to the archive
my_chat = Chat(api_key="sk-1234567890abcdef...", title="Session One")
archive.add(my_chat)

# 3. Save the archive to disk
archive.save()

# 4. Retrieve data from the archive (asynchronously, in chunks by default)
loaded_data = archive.archive_data # Remember, it's better to use the archive_data attribute instead of retrieve()
for item_id, item_obj in loaded_data.items():
    print(item_id, item_obj)

# 5. Remove the chat by its ID (e.g., 0)
archive.remove(0)
archive.save()  # Reflect changes on disk

# 6. Disable asynchronous loading if you run into concurrency issues
archive.archive_asynchronous = False
```

In this example, we initialize a `CWArchive`, add a `Chat` to it, and then save and retrieve data. If concurrency errors appear due to asynchronous operations, you can either increase `archive_delay` or set `archive_asynchronous` to `False` to force sequential processing.

### Using the Context Manager

```python
from chatweaver import CWArchive, Bot

my_bot = Bot(api_key="sk-1234567890abcdef...", rules="Be helpful!", name="HelperBot")

with CWArchive(path="my_archive.txt") as archive:
    archive.add(my_bot)
    # No need to manually call archive.save()
```

When using CWArchive as a context manager:
- `__enter__` is called at the start of the with block, returning the instance.
- `__exit__` is automatically called at the end, ensuring save() is executed.
