# File Sync Watcher

Односторонняя синхронизация: следит за изменениями в `source` и копирует их в `destination`.

## Установка
```bash
pip install -r requirements.txt
```

## Настройка
Отредактируйте `config.ini`:
```
[source]
path = C:/path/source

[destination]
path = C:/path/destination
```

## Запуск
```bash
python main.py
```
