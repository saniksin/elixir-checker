# Elixir Checker

Софт для автоматической проверки дропа [Elixir](https://claim.elixir.xyz/).

## 📢 Контакты

- Мой Telegram канал: [@cryptosaniksin](https://t.me/cryptosaniksin)
- Чат: [@cryptosaniksin_chat](https://t.me/cryptosaniksin_chat)

## 🐍 Требования

- Python 3.12

## ⚙️ Установка

```sh
# Клонируем репозиторий
git clone https://github.com/saniksin/elixir-checker
cd elixir-checker

# Устанавливаем зависимости
pip install -r requirements.txt
```

## 📂 Импорт файлов

Поместите необходимые файлы в папку `imports`:
- **proxies.txt** (**обязательно**): список прокси в формате `http://login:password@ip:port`
- **wallets.txt** (**обязательно**): список EVM-адресов для проверки.

⚠️ Количество прокси должно быть не меньше количества адресов!

## 🚀 Использование

```sh
python main.py
```

## 📊 Вывод результатов

- Успешные проверки записываются в папку `status` -> `result.txt` в формате:
  ```
  0x123...abc | Eligibility: True | Amount Range: 259.7001942 - 519.4003884
  ```
- Ошибки также записываются в этот файл.
- По завершению работы в консоль выводится таблица с результатами и общая сумма диапазона клейма:
  ```
  Общая сумма Elixir (Range): 259.7001942 - 519.4003884
  ```
