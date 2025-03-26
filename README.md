# ChatWeaver

**ChatWeaver** is a Python library that simplifies the implementation of chatbots powered by OpenAI models. Designed with developers in mind, it provides powerful features and an intuitive interface to enhance the development of conversational AI.

---

## Features

- **Chat History Management**: Easily track and manage conversation context.
- **Message Templates**: Automatically remember and include previous messages in prompts.
- **File Integration**: Add images and PDF files to your prompts seamlessly.
- **Custom Model Support**: Compatible with various OpenAI models.
- **Extensibility**: Flexible architecture for scalable chatbot solutions.

---

## Installation
Install ChatWeaver using pip:

```bash
pip install chatweaver
```

---

## Quick Start

Here’s how you can get started with ChatWeaver:

```python
import chatweaver as cw

model = cw.Model(
    model="gpt-4o", 
    api_key="<Your OpenAI API key here>"
    )

bot = cw.Bot(
    rules=cw.chat_weaver_rules["basic"], 
    name="AiBot", 
    cw_model=model
    )

chat = cw.Chat(
    replies_limit=10, 
    user="Diego", 
    cw_bot=bot
    )

prompt = "Hi how are you?"
print(chat.get_response(prompt=prompt))
```

### Include images and files

You may also include images and files in the prompt by specifying their file paths.
```python
prompt = "Describe the content of the attached image."
image = "path\\to\\image.png"
print(chat.get_response(prompt=prompt, image_path=image))
```

### Implementation of Model Rules

ChatWeaver allows the customization of chatbot behavior through a set of predefined rules, defined in the variable `chat_weaver_rules`. These rules determine the role, style, format, and ethical guidelines the bot must follow. Each rule is designed to suit specific scenarios, enhancing interactivity and consistency in the conversation.

#### Available Rules

1. **basic**: Sets the bot with scientifically accurate and reliable goals. Includes:
   - No text formatting.
   - Friendly and respectful communication.
   - Complete and contextual responses.
   - Strict ethical standards.
2. **default**: Optimizes the bot to keep the conversation flowing in a JSON format. Main features:
   - Single-line responses using `\n`.
   - JSON structure with keys like `reasoning`, `reply`, `result`.
3. **informal_chat**: Adjusts the bot for informal conversations. Key features:
   - Friendly and conversational language.
   - Simple JSON response format.
4. **formal_chat**: Adapts the bot for formal conversations. Includes:
   - Polite and respectful communication.
   - Formal JSON structure.
5. **formal_email**: Optimizes the bot for formal email exchanges. Features:
   - Adherence to email structure with greetings, body, and closing.
   - Detailed JSON responses.

#### Rule Implementation Example

To use a specific rule in your bot:

```python
import chatweaver as cw

model = cw.Model(api_key="<Your OpenAI API key here>")

bot1 = cw.Bot(rules=cw.chat_weaver_rules["basic"], cw_model=model)
bot2 = cw.Bot(rules=cw.chat_weaver_rules["default"], cw_model=model)

prompt = "Hello, how are you?"
response1 = bot1.response(prompt=prompt)["content"]
response2 = bot2.response(prompt=prompt)["content"]

print(f"Response from 'bot1': {response1}\n")
print(f"Response from 'bot2': {response2}")
```

### Saving and retrieving ChatWeaver objects from files
A ChatWeaver object can be saved simply by storing the result of its `repr()` method. To restore the object, use the `load()` method.

```python
# Saving the chat
with open("path\\to\\file", "w") as f:
    f.write(repr(chat))

# Loading the chat
with open("path\\to\\file", "r") as f:
    chat = cw.load(f.read())
```

---

## Requirements
- Python 3.9 or above.
- OpenAI Python library (openai).

---

### New Updates in the Latest Version of the Python Library (0.2.0)

- Chat messages are now stored as `TextNode` objects and can be converted back to dictionaries using `dict(<TextNode object>)`.  
- Each `TextNode` now includes its own creation date and time.  
- Each chat session now has its own creation date and time.  
- Each chat session now has its own `cost` in tokens.
- Introduced a new `load()` function that takes the result of `repr()` from a `ChatWeaver` object and returns the object itself. This is useful for saving `Chat`/`Bot`/`Model` data in separate files and restoring them when needed.  

