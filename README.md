# SimpleAI

**SimpleAI** is a lightweight chatbot framework that allows for easy customization and learning based on user input. The chatbot can be configured to learn new responses or operate in a manual mode where all responses are pre-defined. It’s designed for simple use cases but allows flexibility for advanced users.

## Features

- **Learning Mode**: Automatically learns new phrases and their corresponding responses.
- **Manual Mode**: Requires predefined responses and adds them manually.
- **Configurable Filters**: Add custom filters and handlers to control what the bot learns and how it responds.
- **Monitor Performance**: Track response times and question logs.
- **Backup System**: Automatically creates backups of your model data to prevent loss.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Mateopowy/SimpleAI.git
cd SimpleAI
```

2. Install dependencies (if any):
```bash
pip install -r requirements.txt
```

3. Create a folder for AI models:
```bash
mkdir -p "models"
```

4. Create a basic model file (example: `my-model.basic-model`):
```json
{
    "hello": ["Hi!", "Hello there!"],
    "how are you?": ["I'm fine, thank you!"]
}
```

## Usage

To run the chatbot, simply use the following code:

```python
# Create configuration
config = Configuration.default()
config.models_path = 'models'

# Create AI object
my_ai = AI(
    model='my-model',
    configuration=config
)

while True:
    # User input:
    inp = input('You: ')

    # Analyze:
    resp, info = my_ai.ask(inp)

    # Reply:
    print(f'AI: {resp}')
```

### Example interaction:

```bash
You: Hello
AI: Hi!

You: How are you?
AI: I'm fine, thank you!
```

## Configuration

The bot comes with multiple configuration options:

- **TrainMode**: Choose between `chat` (default) or `man` (manual) mode.
- **IfUnknownType**: Choose between `random_response` or `return_error` when an unknown input is given.
- **Monitor**: Keeps track of questions, response times, and knowledge records.
- **Learning**: Enable or disable learning based on your preference.

### Predefined Configurations:

1. **Default Configuration**: Chat mode with learning enabled.
2. **Secure Configuration**: Ignores Discord invites and links for safety.
3. **Chat-Only Configuration**: Learning is disabled, and responses are predefined.
4. **Manual Learning Mode**: Allows only manual training.

```python
config = Configuration.chat_only()
config.monitor = Monitor(limit=50)

my_ai = AI(model='my-model', configuration=config)
```

## Backup and Restore

SimpleAI automatically creates a backup when new data is saved. Backups are stored in the `backups/` directory.
