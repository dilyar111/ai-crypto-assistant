def extract_token_name(query):
    # Простой способ: находим последнее слово
    return query.split()[-1].strip("?").lower()
