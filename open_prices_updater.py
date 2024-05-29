# from send_all_signals import process_signal
#
# process_signal('signals_3bars_growing_volumes', '2024-03-28')
import os
import json
import datetime
from binance.client import Client
from binance.enums import *
from src.config_handler import TIMEFRAMES, BINANCE_API_KEY, BINANCE_Secret_KEY
import src.logger as custom_logging

# Создаем экземпляр клиента
client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_Secret_KEY)


def delete_all_files_from_folder(folder_name: str):
    """
    удалить все файлы из каталога
    """
    # Проверяем, существует ли каталог
    if not os.path.exists(folder_name):
        print(f"Folder {folder_name} not found.")
        return

    # Перебираем все файлы в каталоге
    for filename in os.listdir(folder_name):
        file_path = os.path.join(folder_name, filename)
        try:
            # Если это файл, удаляем его
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('File %s delete error: %s' % (file_path, e))

def store_dict_to_file(data: dict):
    """
    Сохранить словарь в файл (json-формат)
    """
    delete_all_files_from_folder('day_open_price')
    file_name = f"day_open_price/{datetime.date.today().isoformat()}.txt"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        print(f'Day open prices stored to file "{file_name}".')
        custom_logging.info(f'Day open prices stored to file "{file_name}".')
        custom_logging.info(
            f'**************************************************************************************')

# Функция для получения цен открытия
def update_day_opening_prices():
    """
    обновить цены открытия дневного бара
    """
    # Получаем информацию о всех фьючерсах
    exchange_info = client.futures_exchange_info()
    symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['contractType'] == 'PERPETUAL'
               and symbol['status'] == 'TRADING']

    opening_prices = {}
    for symbol in symbols:
        # Получаем котировки за последние 24 часа
        klines = client.futures_klines(symbol=symbol, interval=KLINE_INTERVAL_1DAY, limit=1)
        # Цена открытия - это первый элемент в каждом kline
        opening_price = klines[0][1]
        opening_prices[symbol] = float(opening_price)
    store_dict_to_file(opening_prices)
    return opening_prices

# Получаем и выводим цены открытия
if __name__ == '__main__':
    opening_prices = update_day_opening_prices()
