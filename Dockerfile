# Використовуємо Python 3.12
FROM python:3.12.1

# Встановлюємо змінну середовища для робочої директорії
ENV APP_HOME /app

# Встановлюємо робочу директорію
WORKDIR $APP_HOME

# Копіюємо всі файли у контейнер
COPY . $APP_HOME

# Встановлюємо залежності
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Відкриваємо порт 3000
EXPOSE 3000

# Запускаємо застосунок
CMD ["python", "main.py"]