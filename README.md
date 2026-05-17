# Travel Time Map — Limassol → Alber Blanc

Сбор данных о времени в пути между 34 точками в Лимассоле и рестораном Alber Blanc с визуализацией на интерактивной карте.

## Как работает

- **collector.py** — собирает время в пути через Google Routes API (в обоих направлениях)
- **build_map.py** — генерирует `index.html` с интерактивной картой Leaflet

## Быстрый старт

```bash
# Установка
uv sync

# Настройка API ключа
echo "GOOGLE_API_KEY=your_key_here" > .env

# Тестовый сбор
uv run python collector.py --once

# Генерация карты
uv run python build_map.py
open index.html
```

## Сбор данных

```bash
# Непрерывный сбор: каждые 30 мин с 7:00 до 20:00, 2 дня
uv run python collector.py

# Или указать количество дней
uv run python collector.py --days 3
```

Данные сохраняются в `data/YYYY-MM-DD.json`.

## Карта

- Маркеры с цветовым градиентом: зелёный (< 10 мин), жёлтый (10–20 мин), красный (> 20 мин)
- Время в минутах на каждом маркере
- Переключение направления: к Alber Blanc / от Alber Blanc
- Слайдер по времени сбора
- Ссылка на маршрут в Google Maps в popup
