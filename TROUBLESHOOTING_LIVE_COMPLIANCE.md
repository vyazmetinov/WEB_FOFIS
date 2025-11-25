# 🔧 Troubleshooting - Live Compliance

## Проблемы и решения

---

## ❌ Проблема 1: Live Compliance не отображается

### Симптомы
- В Playback Controls нет блока "Live Compliance"
- Страница выглядит как раньше

### Решение

```bash
# Шаг 1: Принудительное обновление браузера
Ctrl+F5 (Windows/Linux)
Cmd+Shift+R (Mac)

# Шаг 2: Очистить кэш браузера
1. F12 → Application → Clear Storage → Clear site data
2. Обновить страницу

# Шаг 3: Проверить, что сервер перезапущен
Ctrl+C в терминале
python manage.py runserver
```

### Проверка

Откройте Console (F12) и выполните:
```javascript
document.getElementById('live-compliance')
```

Должно вернуть HTML элемент, а не `null`

---

## ❌ Проблема 2: Compliance не обновляется при воспроизведении

### Симптомы
- Блок Live Compliance виден
- Но значение остается "---%" или "0.0%"
- Не меняется при нажатии Play

### Решение

#### Проверка 1: Console Errors

```javascript
// Откройте Console (F12)
// Нажмите Play и посмотрите на ошибки

// Типичные ошибки:
// ❌ "Cannot read property 'cpp_compliant' of undefined"
// → Данные траектории некорректны

// ❌ "updateLiveCompliance is not defined"
// → Нужно Ctrl+F5
```

#### Проверка 2: Данные траектории

```javascript
// В Console (F12)
console.log(currentFlightCase);
console.log(currentFlightCase.trajectory_data[0]);

// Должно показать объект с полями:
// {
//   latitude: 50.0,
//   longitude: 10.0,
//   altitude: 1000.0,
//   speed: 250.0,
//   time_seconds: 0,
//   deviation: 125.5,
//   allowed_deviation: 500.0,
//   allowed_speed: 300.0,
//   cpp_compliant: true  ← ВАЖНО!
// }
```

#### Проверка 3: C++ программа

```bash
cd /Users/ivan/PycharmProjects/FOFIS/cpp

# Проверить компиляцию
make

# Проверить работу
./trajectory_validator \
  50.0 10.0 1000.0 250.0 \
  50.1 10.1 1000.0 \
  50.2 10.2 1000.0 \
  500.0 300.0

# Должен вывести 3 числа:
# 13214.51 0.00 1
#  ↑       ↑    ↑
#  dev   speed  compliant
```

---

## ❌ Проблема 3: Compliance всегда 0%

### Симптомы
- Live Compliance отображается
- Но показывает 0.0% на протяжении всего воспроизведения

### Причина
C++ не возвращает `is_compliant` или все точки некомплаентны

### Решение

#### Шаг 1: Проверка C++ вывода

```bash
cd cpp
./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0

# ПРАВИЛЬНЫЙ вывод (3 числа):
13214.51 0.00 1

# НЕПРАВИЛЬНЫЙ вывод (2 числа):
13214.51 0.00

# Если 2 числа → нужно перекомпилировать!
```

#### Шаг 2: Перекомпиляция C++

```bash
cd /Users/ivan/PycharmProjects/FOFIS/cpp
rm trajectory_validator
make

# Проверить снова
./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0
```

#### Шаг 3: Перезагрузка данных

```bash
# Удалить существующие файлы
cd /Users/ivan/PycharmProjects/FOFIS
rm -rf media/corridors/* media/trajectories/*

# Очистить БД
python manage.py shell
>>> from monitoring.models import FlightCase
>>> FlightCase.objects.all().delete()
>>> exit()

# Перезапустить сервер
python manage.py runserver

# Загрузить файлы заново
```

---

## ❌ Проблема 4: Compliance не меняет цвет

### Симптомы
- Compliance обновляется (цифры меняются)
- Но цвет остается синим/серым
- Не становится зеленым/оранжевым/красным

### Решение

#### Проверка в Console

```javascript
// Откройте Console (F12)
const elem = document.getElementById('live-compliance-value');
console.log(elem.style.color);

// Если пусто → функция не отрабатывает
// Проверьте:
console.log(window.updateLiveCompliance);
// Должна быть функция, не undefined
```

#### Принудительная установка

```javascript
// В Console попробуйте вручную:
const valueElem = document.getElementById('live-compliance-value');
const fillElem = document.getElementById('live-compliance-fill');

valueElem.style.color = '#4CAF50';
fillElem.style.backgroundColor = '#4CAF50';

// Если это работает → проблема в логике updateLiveCompliance
// Если не работает → проблема с элементами
```

---

## ❌ Проблема 5: Progress Bar не заполняется

### Симптомы
- Цифры Compliance обновляются
- Цвет меняется
- Но progress bar остается пустым

### Решение

```javascript
// В Console (F12)
const fill = document.getElementById('live-compliance-fill');
console.log(fill);
console.log(fill.style.width);

// Установить вручную
fill.style.width = '50%';
fill.style.backgroundColor = '#4CAF50';

// Если работает → Ctrl+F5 для обновления
// Если не работает → проверьте CSS
```

---

## ❌ Проблема 6: Compliance не сбрасывается при Stop

### Симптомы
- Нажали Play → Compliance вырос до 85%
- Нажали Stop → Compliance остался 85%
- Должен сброситься до 0%

### Решение

```javascript
// Проверка в Console
console.log(window.resetLiveCompliance);
// Должна быть функция

// Вызвать вручную
resetLiveCompliance();

// Если сбросилось → все работает, просто Ctrl+F5
// Если нет → проверьте stopPlayback()
```

---

## ❌ Проблема 7: Ошибка 500 при загрузке файлов

### Симптомы
- Загружаете corridor + trajectory
- Вместо Compliance появляется "Error"
- В Console: "HTTP 500 Internal Server Error"

### Решение

#### Проверка логов Django

```bash
# В терминале с сервером посмотрите на ошибки
# Типичные ошибки:

# ❌ FileNotFoundError: cpp/trajectory_validator
cd cpp && make

# ❌ ValueError: not enough values to unpack
# → C++ вывод некорректен, перекомпилируйте

# ❌ PermissionError
chmod +x cpp/trajectory_validator

# ❌ FloatField cannot be null
python manage.py migrate
```

#### Перезапуск с чистого листа

```bash
# Остановить сервер
Ctrl+C

# Применить миграции
python manage.py migrate

# Проверить C++
cd cpp
make
./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0

# Очистить медиа
cd ..
rm -rf media/corridors/* media/trajectories/*

# Запустить сервер
python manage.py runserver
```

---

## ✅ Контрольный чек-лист

Перед запуском убедитесь:

- [ ] C++ скомпилирован: `cd cpp && make`
- [ ] C++ работает: `./trajectory_validator ...` выводит 3 числа
- [ ] Миграции применены: `python manage.py migrate`
- [ ] Сервер перезапущен: `Ctrl+C` → `python manage.py runserver`
- [ ] Браузер обновлен: `Ctrl+F5`
- [ ] Console открыта: `F12`
- [ ] Нет ошибок в Console

Во время теста проверьте:

- [ ] Блок Live Compliance виден в Playback Controls
- [ ] При нажатии Play значение меняется от 0%
- [ ] Progress bar заполняется
- [ ] Цвет меняется в зависимости от значения
- [ ] При Stop сбрасывается до 0%
- [ ] При перемотке пересчитывается

---

## 🐛 Полный сброс (если ничего не помогло)

```bash
# 1. Остановить сервер
Ctrl+C

# 2. Перекомпилировать C++
cd /Users/ivan/PycharmProjects/FOFIS/cpp
rm trajectory_validator
make clean
make

# Проверить
./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0
# Должно вывести 3 числа: deviation speed is_compliant

# 3. Очистить БД и медиа
cd ..
rm db.sqlite3
rm -rf media/corridors/* media/trajectories/*

# 4. Пересоздать БД
python manage.py migrate

# 5. Запустить сервер
python manage.py runserver

# 6. В браузере:
# - Ctrl+Shift+Delete → Clear cache
# - Ctrl+F5 на http://127.0.0.1:8000/
# - F12 → Console
# - Загрузить файлы заново
```

---

## 📞 Как получить помощь

### 1. Соберите информацию

```bash
# Python версия
python --version

# Django версия
python manage.py version

# C++ компиляция
cd cpp && make && ./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0

# Браузер
# → Версия браузера (Chrome/Firefox/Safari)
```

### 2. Сохраните логи

```bash
# Django errors
python manage.py runserver > server.log 2>&1

# Browser console
# F12 → Console → Скопировать все сообщения
```

### 3. Проверьте файлы

```bash
# Проверить, что файлы обновлены
grep "live-compliance" templates/index.html
grep "updateLiveCompliance" templates/index.html
grep "is_compliant" cpp/trajectory_validator.cpp
```

---

## ⚡ Быстрые команды

### Перезапуск всего

```bash
cd /Users/ivan/PycharmProjects/FOFIS
Ctrl+C
cd cpp && make && cd ..
python manage.py runserver
# В браузере: Ctrl+F5
```

### Проверка C++

```bash
cd cpp
./trajectory_validator 50.0 10.0 1000.0 250.0 50.1 10.1 1000.0 50.2 10.2 1000.0 500.0 300.0 | wc -w
# Должно вывести: 3 (три числа)
```

### Проверка JS

```javascript
// Console (F12)
console.log(typeof updateLiveCompliance);  // "function"
console.log(document.getElementById('live-compliance'));  // HTML element
console.log(currentFlightCase?.trajectory_data?.[0]?.cpp_compliant);  // true/false
```

---

## 🎯 Итого

Большинство проблем решаются:

1. **Ctrl+F5** - принудительное обновление браузера
2. **cd cpp && make** - перекомпиляция C++
3. **python manage.py runserver** - перезапуск сервера

Если проблема сохраняется → используйте **Полный сброс** выше.

---

**Удачи! 🚀**




