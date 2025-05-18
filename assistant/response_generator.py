import requests

# Адрес локального Ollama сервера
OLLAMA_URL = "http://127.0.0.1:11434"

def generate_response(prompt, model="llama2"):
    """
    Отправляет запрос на локальный Ollama сервер
    и возвращает текст ответа модели.
    
    :param prompt: Строка с запросом к модели
    :param model: Название модели (по умолчанию "llama2")
    :return: Ответ модели (строка)
    """
    url = f"{OLLAMA_URL}/v1/completions"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
    # В зависимости от версии Ollama API структура может отличаться,
    # обычно ответ содержится в result["choices"][0]["text"]
    return result["choices"][0]["text"]

# Пример запуска, если файл запускается напрямую
if __name__ == "__main__":
    test_prompt = "Расскажи о криптовалюте Ethereum."
    print(generate_response(test_prompt))
