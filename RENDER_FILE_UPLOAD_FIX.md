# 🔧 Исправление загрузки файлов на Render.com

## 🐛 Проблема
На Render.com загрузка файлов не работает (upload failed), хотя локально всё работает.

## ✅ Что было исправлено:

### 1. **Добавлена переменная окружения MEDIA_ROOT**
```yaml
envVars:
  - key: MEDIA_ROOT
    value: /opt/render/project/src/media
```
Теперь Django знает, куда сохранять загруженные файлы.

### 2. **Создание директорий в build скрипте**
```bash
mkdir -p /opt/render/project/src/media/corridors
mkdir -p /opt/render/project/src/media/trajectories
chmod -R 755 /opt/render/project/src/media
```
Директории для файлов создаются при деплое с правильными permissions.

### 3. **Настроены CORS headers**
```python
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'content-type',
    'x-csrftoken',
    ...
]
```
Теперь браузер может отправлять файлы через AJAX.

### 4. **Добавлены CSRF Trusted Origins**
```python
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://web-fofis.onrender.com',
]
```
Django принимает запросы с вашего Render домена.

### 5. **Увеличены лимиты загрузки файлов**
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

### 6. **Добавлено логирование**
Теперь можно диагностировать проблемы через логи Render:
```python
logger.info(f"Received file upload request...")
logger.error(f"Error creating flight case...")
```

---

## 🚀 Как применить исправления:

### 1. Закоммитьте изменения:
```bash
cd /Users/ivan/PycharmProjects/FOFIS
git add -A
git commit -m "Fix file upload on Render: add MEDIA_ROOT, CORS, CSRF settings"
git push origin main
```

### 2. В Render Dashboard:

#### Если создавали вручную:
1. Откройте ваш сервис WEB_FOFIS
2. Settings → Environment Variables
3. Добавьте вручную (если нет):
   ```
   MEDIA_ROOT=/opt/render/project/src/media
   ```
4. Settings → Disks → убедитесь что disk подключен:
   - Mount Path: `/opt/render/project/src/media`
   - Size: 1 GB
5. Manual Deploy → Clear build cache & deploy

#### Если создавали через Blueprint:
Просто сделайте push - Render автоматически задеплоит изменения!

---

## 🔍 Проверка после деплоя:

### 1. Проверьте логи в Render:
- Откройте Logs tab
- Найдите строки:
  ```
  📁 Creating media directories...
  ✓ Media directories created
  ```

### 2. Проверьте переменные окружения:
В Shell tab выполните:
```bash
echo $MEDIA_ROOT
# Должно вывести: /opt/render/project/src/media

ls -la /opt/render/project/src/media
# Должны быть: corridors/ и trajectories/
```

### 3. Проверьте permissions:
```bash
ls -ld /opt/render/project/src/media
# Должно быть: drwxr-xr-x (755)
```

### 4. Тест загрузки через curl:
```bash
curl -X POST https://web-fofis.onrender.com/api/flight-cases/ \
  -H "Content-Type: multipart/form-data" \
  -F "corridor_file=@sample_data/corridor.txt" \
  -F "trajectory_file=@sample_data/trajectory.txt"
```

### 5. Тест через браузер:
1. Откройте https://web-fofis.onrender.com/
2. Загрузите файлы из sample_data/
3. Должны появиться в таблице

---

## 🐛 Если всё еще не работает:

### Проблема 1: "403 Forbidden"
**Причина:** CSRF token
**Решение:** Убедитесь что в CSRF_TRUSTED_ORIGINS есть ваш домен:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://web-fofis.onrender.com',  # Ваш реальный URL
]
```

### Проблема 2: "Permission denied"
**Причина:** Нет прав на запись
**Решение:** В Shell:
```bash
chmod -R 755 /opt/render/project/src/media
```

### Проблема 3: "No such file or directory"
**Причина:** Директории не созданы
**Решение:** В Shell:
```bash
mkdir -p /opt/render/project/src/media/corridors
mkdir -p /opt/render/project/src/media/trajectories
```

### Проблема 4: Disk не подключен
**Причина:** Disk не был создан или не подключен
**Решение:**
1. Settings → Disks
2. Add Disk:
   - Name: `fofis-media`
   - Mount Path: `/opt/render/project/src/media`
   - Size: 1 GB
3. Deploy

### Проблема 5: CORS errors в браузере
**Причина:** CORS не настроен
**Решение:** Убедитесь что в requirements.txt есть:
```
django-cors-headers==4.3.0
```
И в INSTALLED_APPS есть `'corsheaders'`

---

## 📊 Проверка через логи:

После загрузки файла в Render Logs должны появиться:
```
Received file upload request. Files: dict_keys(['corridor_file', 'trajectory_file'])
Saving flight case...
Flight case saved with ID: 1
Corridor file: corridors/corridor_abc123.txt
Trajectory file: trajectories/trajectory_xyz456.txt
Starting file processing...
Processing result: True
"POST /api/flight-cases/ HTTP/1.1" 201 1234
```

Если видите ошибки, они будут в формате:
```
Error creating flight case: [ошибка]
"POST /api/flight-cases/ HTTP/1.1" 400 123
```

---

## ✅ Контрольный список:

- [ ] MEDIA_ROOT в Environment Variables
- [ ] Disk подключен к `/opt/render/project/src/media`
- [ ] Директории созданы в build скрипте
- [ ] CORS настроен (corsheaders в INSTALLED_APPS)
- [ ] CSRF_TRUSTED_ORIGINS содержит ваш домен
- [ ] Изменения закоммичены и запушены
- [ ] Render задеплоил новую версию
- [ ] Логи не показывают ошибок

---

## 🎉 Результат

После применения всех исправлений:
- ✅ Файлы загружаются на Render
- ✅ Сохраняются в persistent disk
- ✅ Обрабатываются C++ валидатором
- ✅ Отображаются на карте
- ✅ Доступны между деплоями

---

## 📞 Дополнительная помощь

Если проблема не решена, проверьте:
1. **Render Logs** - полные логи ошибок
2. **Browser Console** (F12) - CORS/CSRF ошибки
3. **Network Tab** - HTTP статусы и ответы
4. **Shell** - проверьте файловую систему напрямую

Логи покажут точную причину проблемы! 🔍

