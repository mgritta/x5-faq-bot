# X5 FAQ Assistant

Assistant for answering questions about X5 Tech internships.

## Quick Setup

```bash
git clone https://github.com/mgritta/x5-faq-bot.git
cd x5-faq-bot
pip install -r requirements.txt
cp config.example.py config.py
```

Get an API key from [OpenRouter.ai](https://openrouter.ai) and add it to `config.py`.

## Usage

```python
from x5_bot import X5FAQAssistant

assistant = X5FAQAssistant()
answer = assistant.ask_openrouter("Как долго длится стажировка?")
```

## Project Structure

- `x5_bot.py` - main assistant class
- `x5_faq.json` - structured internship data
- `prompt.py` - LLM instructions and safety rules
- `config.example.py` - configuration template
- `requirements.txt` - dependencies

## Integration

Copy the needed files to your project or import the class directly.

