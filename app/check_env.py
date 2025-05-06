from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# Получаем все переменные окружения
env_vars = os.environ

# Выводим все переменные окружения, загруженные с .env
for key, value in env_vars.items():
    print(f'{key}: {value}')