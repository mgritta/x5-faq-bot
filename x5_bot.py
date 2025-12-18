import requests
import json
import time
from typing import Dict, List, Optional

class X5FAQAssistant:
    def __init__(self):
        try:
            from config import OPENROUTER_API_KEY, OPENROUTER_API_URL, FAQ_FILE
            self.api_key = OPENROUTER_API_KEY
            self.api_url = OPENROUTER_API_URL
            self.faq_file = FAQ_FILE
        except ImportError:
            print("Ошибка с API_KEY")
            exit(1)
        
        self.faq_data = self.load_faq(self.faq_file)
        self.prompt_template = self.load_prompt()
    
    def load_faq(self, filepath: str) -> Dict:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл {filepath} не найден")
        except json.JSONDecodeError:
            print(f"Ошибка чтения JSON в файле {filepath}")
    
    def load_prompt(self) -> str:
        try:
            from prompt import PROMPT_TEMPLATE
            return PROMPT_TEMPLATE
        except ImportError:
            print("Файл prompt.py не найден")
            return "Отвечай на вопросы о стажировках в X5 Tech."
    
    def format_context_for_llm(self) -> str:
        context = f"{self.faq_data.get('company', 'X5 Tech')} - Программа стажировки\n"
        context += f"Актуально на: {self.faq_data.get('last_updated', '2024-12-17')}\n\n"
        
        if 'about_company' in self.faq_data:
            about = self.faq_data['about_company']
            context += "О компании:\n"
            if 'key_facts' in about:
                context += "Ключевые факты о компании:\n"
                facts_mapping = {
                    'specialists': 'Специалистов',
                    'customers': 'Покупателей',
                    'data_in_storage': 'Данных в хранилище',
                    'physical_servers': 'Физических серверов'
                }
                
                for key, value in about['key_facts'].items():
                    if key in facts_mapping:
                        context += f"{facts_mapping[key]}: {value}\n"
                context += "\n"
        
        if 'general_faq' in self.faq_data and self.faq_data['general_faq']:
            context += "Общие вопросы о стажировке:\n"
            for item in self.faq_data['general_faq']:
                context += f"{item.get('question', '')}\n"
                context += f"Ответ: {item.get('answer', '')}\n\n"
        
        if 'vacancies' in self.faq_data and self.faq_data['vacancies']:
            context += "Доступные вакансии:\n"
            for vac in self.faq_data['vacancies'][:5]:
                context += f"{vac.get('title', '')}\n"
                context += f"Отдел: {vac.get('department', '')}\n"
                
                if 'tasks' in vac and vac['tasks']:
                    context += f"Задачи: {', '.join(vac['tasks'][:2])}\n"
                
                if 'requirements' in vac and vac['requirements']:
                    context += f"Требования: {', '.join(vac['requirements'][:3])}\n"
                
                context += "\n"
        
        if 'benefits_shared' in self.faq_data and self.faq_data['benefits_shared']:
            context += "Преимущества работы в X5 Tech:\n"
            for i, benefit in enumerate(self.faq_data['benefits_shared'][:7], 1):
                context += f"{i}. {benefit}\n"
        
        if 'about_company' in self.faq_data and 'office_addresses' in self.faq_data['about_company']:
            context += "\nОфисы компании:\n"
            for location, address in self.faq_data['about_company']['office_addresses'].items():
                context += f"{location}: {address}\n"
        
        context += f"\nКонтакты для вопросов по стажировкам:\n{self.faq_data['general_faq'][-1].get('answer', 'internship@x5.tech')}\n"
        
        return context
    
    def ask_openrouter(self, question: str) -> str:
        context = self.format_context_for_llm()
        prompt = self.prompt_template.format(context=context, question=question)
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://x5.tech",
                    "X-Title": "X5 FAQ Assistant"
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Ты ассистент для ответа на вопросы по стажировкам."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 350,
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                },
                timeout=20
            )
                        
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                return answer
                
            elif response.status_code == 429:
                return "Слишком много запросов. Подождите немного или попробуйте позже."
                
            elif response.status_code == 401:
                return "Неверный API ключ. Проверьте config.py"
                
            else:
                error_text = response.text[:150] if response.text else "No error details"
                return f"Ошибка API ({response.status_code}): {error_text}"
                
        except requests.exceptions.Timeout:
            return "Таймаут запроса. Попробуйте снова."
            
        except requests.exceptions.ConnectionError:
            return "Ошибка подключения. Проверьте интернет."
            
        except Exception as e:
            return f"Неожиданная ошибка: {str(e)[:100]}"
    
    def fallback_answer(self, question: str) -> str:
        q_lower = question.lower()
        
        for item in self.faq_data.get('general_faq', []):
            question_text = item.get('question', '').lower()
            if any(word in q_lower for word in question_text.split()[:3]):
                return item.get('answer', '') + f"\n\nПишите на: {self.faq_data['general_faq'][-1].get('answer', 'internship@x5.tech')}"
        
        keyword_responses = {
            'python': "Для Python-стажёра: Python 3, PostgreSQL, FastAPI, Airflow. Задачи: разработка бекенда, ETL-пайплайны.",
            'javascript': "Для JavaScript-стажёра: Node.js, Git, веб-архитектура. Задачи: разработка решений управления производством.",
            'data science': "Для Data Science: Python, SQL, статистика. Задачи: A/B-тесты, анализ данных, исследования.",
            'оплата': "Стажировка оплачиваемая — белая зарплата. Точная сумма зависит от направления.",
            'удаленно': "Доступны форматы: удалённо, гибрид или офис в Москве, Иннополисе, Ижевске.",
            'опыт': "Опыт не требуется. Достаточно базовых знаний и готовности учиться.",
            'офис': "Офисы в Москве (Калитники, Оазис), Иннополисе и Ижевске. Адреса в информации о компании.",
            'компания': "X5 Tech — IT-компания, 5000+ специалистов, 1 млрд чеков в день, 80 млн покупателей."
        }
        
        for keyword, response in keyword_responses.items():
            if keyword in q_lower:
                return f"{response}\n\nПишите на: {self.faq_data['general_faq'][-1].get('answer', 'internship@x5.tech')}"
        
        return f"Уточните вопрос о стажировках в X5 Tech. Для информации пишите на {self.faq_data['general_faq'][-1].get('answer', 'internship@x5.tech')}"
    
    def interactive_mode(self):
        while True:
            try:
                question = input("\nВопрос: ").strip()
                
                if question.lower() in ['выход', 'exit', 'quit', 'q']:
                    break
                
                if question.lower() in ['помощь', 'help', '?']:
                    print("\nДоступные команды:")
                    print(" • задайте вопрос о стажировке")
                    print(" • 'выход' - завершить работу")
                    continue
                
                if not question:
                    continue
                
                print("Ищу ответ...", end="", flush=True)
                
                for _ in range(3):
                    print(".", end="", flush=True)
                    time.sleep(0.2)
                
                answer = self.ask_openrouter(question)
                print(f"\nОтвет: {answer}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nОшибка: {e}")
                print("Попробуйте ещё раз.")

if __name__ == "__main__":
    try:
        bot = X5FAQAssistant()
        print("Команды: 'помощь', 'выход'")
        bot.interactive_mode()
    except Exception as e:
        print(f"\nОшибка запуска: {e}")