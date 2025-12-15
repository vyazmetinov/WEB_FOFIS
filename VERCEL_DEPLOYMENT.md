# Деплой FOFIS на Vercel

## Шаги для деплоя

### 1. Подготовка проекта

Все необходимые файлы уже созданы:
- ✅ `vercel.json` - конфигурация Vercel
- ✅ `build.sh` - скрипт сборки
- ✅ `.vercelignore` - файлы для игнорирования
- ✅ `requirements.txt` - зависимости Python (включая gunicorn)

### 2. Установка Vercel CLI (опционально)

Если хотите деплоить через командную строку:

```bash
npm install -g vercel
```

### 3. Деплой через Vercel Dashboard (рекомендуется)

1. Зайдите на [vercel.com](https://vercel.com) и войдите через GitHub
2. Нажмите "Add New Project"
3. Импортируйте ваш GitHub репозиторий FOFIS
4. Vercel автоматически определит настройки из `vercel.json`
5. Добавьте переменные окружения (Environment Variables):
   - `SECRET_KEY`: новый секретный ключ Django
   - `DEBUG`: `False` для продакшена
   - `ALLOWED_HOSTS`: ваш домен на Vercel (например, `your-app.vercel.app`)
6. Нажмите "Deploy"

### 4. Деплой через CLI

Если используете Vercel CLI:

```bash
cd /Users/ivan/PycharmProjects/FOFIS
vercel login
vercel
```

### 5. Настройка переменных окружения

В Dashboard Vercel:
1. Перейдите в Settings → Environment Variables
2. Добавьте:
   ```
   SECRET_KEY=ваш-новый-секретный-ключ
   DEBUG=False
   ALLOWED_HOSTS=ваш-домен.vercel.app
   ```

### 6. После успешного деплоя

Проверьте что работает:
- `/` - главная страница
- `/api/test-upload/` - API для загрузки
- `/api/cases/` - список случаев
- `/static/` - статические файлы

## Важные замечания

### База данных
⚠️ SQLite на Vercel работает только в read-only режиме после деплоя.

**Рекомендуется перейти на PostgreSQL:**

1. Создайте БД на [neon.tech](https://neon.tech) (бесплатный tier)
2. Добавьте в `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```
3. Обновите настройки БД в `settings.py`:
   ```python
   import dj_database_url
   
   DATABASES = {
       'default': dj_database_url.config(
           default='sqlite:///db.sqlite3',
           conn_max_age=600
       )
   }
   ```
4. Добавьте в Vercel env:
   ```
   DATABASE_URL=postgresql://user:pass@host/db
   ```

### Media файлы
⚠️ Файлы, загруженные в `/media/`, не сохраняются между деплоями.

**Рекомендуется использовать S3 или Cloudinary для хранения медиа файлов.**

### C++ валидатор
⚠️ C++ executable может не работать на Vercel из-за ограничений serverless окружения.

**Возможные решения:**
1. Переписать валидатор на Python
2. Использовать внешний API для валидации
3. Использовать другой хостинг (Railway, Render, DigitalOcean)

## Альтернативные платформы

Если Vercel не подходит из-за ограничений:

1. **Railway** - поддерживает полноценные контейнеры
2. **Render** - хороший free tier
3. **Fly.io** - поддержка Docker
4. **PythonAnywhere** - специально для Django

## Проверка деплоя

После деплоя проверьте логи:
```bash
vercel logs
```

## Откат

Если что-то пошло не так:
```bash
vercel rollback
```


