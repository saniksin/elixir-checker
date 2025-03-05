import os
import sys
import asyncio
from pathlib import Path

from loguru import logger


# Определяем путь и устанавливаем root dir
if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

# Импорт
IMPORT_DIR = os.path.join(ROOT_DIR, 'imports')
EVM_ADDRESSES = os.path.join(IMPORT_DIR, 'wallets.txt')
PROXIES = os.path.join(IMPORT_DIR, 'proxies.txt')

# STATUS
STATUS_DIR = os.path.join(ROOT_DIR, 'status')
RESULT = os.path.join(STATUS_DIR, 'result.txt')
LOGGER = os.path.join(STATUS_DIR, 'log.txt')


# Кол-во выполненных асинхронных задач, блокировщий задач asyncio
completed_tasks = [0]
remaining_tasks = [0]
tasks_lock = asyncio.Semaphore(1)

# Логер
logger.add(LOGGER, format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}', level='DEBUG')
