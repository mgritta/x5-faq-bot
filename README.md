# X5 FAQ Assistant

Assistant for answering questions about X5 Tech internships. Provides both console interface and REST API.

## Quick Setup

```bash
git clone https://github.com/mgritta/x5-faq-bot.git
cd x5-faq-bot
pip install -r requirements.txt
cp config.example.py config.py
```

Get an API key from [OpenRouter.ai](https://openrouter.ai) and add it to `config.py` (copy from `config.example.py`).

## Usage Options

### 1. Console Interface
```bash
python x5_bot.py
```

### 2. REST API Server
```bash
python api.py
```
Server runs on `http://localhost:5001`

### 3. Using the API
```python
import requests

response = requests.post('http://localhost:5001/ask',
                        json={'question': 'Как долго длится стажировка?'})

answer = response.json()['answer']
print(answer)
```

### 4. Direct Class Import
```python
from x5_bot import X5FAQAssistant

assistant = X5FAQAssistant()
answer = assistant.ask_llm("Как долго длится стажировка?")
```

## Endpoints

`POST /ask` - ask questions about internships
  ```bash
  curl -X POST http://localhost:5001/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "Your question"}'
  ```


## Project Structure

- `x5_bot.py` - Main assistant class with console interface
- `api.py` - REST API server (Flask)
- `x5_faq.json` - Structured internship data
- `prompt.py` - LLM instructions and safety rules
- `config.example.py` - Configuration template
- `requirements.txt` - Dependencies (requests, flask)