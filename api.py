from flask import Flask, request, jsonify, Response
from x5_bot import X5FAQAssistant
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

assistant = X5FAQAssistant()

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Нет данных в запросе'}), 400
        
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Поле question обязательно'}), 400
        
        answer = assistant.ask_llm(question)
        
        return Response(
            json.dumps({
                'question': question,
                'answer': answer,
                'status': 'success'
            }, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'X5 FAQ API'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)