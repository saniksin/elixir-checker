import asyncio
import json
import pandas as pd
from tabulate import tabulate
from utils.import_info import get_info
from data.config import EVM_ADDRESSES, PROXIES, logger, tasks_lock, RESULT
from data.session import BaseAsyncSession
from data.settings import NUMBER_OF_ATTEMPTS, ASYNC_TASK_IN_SAME_TIME

results = []

async def save_result(address, amount_start, amount_end, error=None):
    if amount_start is not None and amount_end is not None:
        amount_range = f"{amount_start} - {amount_end}"
        if not amount_start and not amount_end:
            status = "❌ Success: Not Eligible"
        else:
            status = "✅ Success: Eligible"
    else:
        amount_range = "0 - 0" if error == "Not Eligible" else "N/A"
        status = f"❌ Error: {error}"

    result = {
        "Address": address,
        "Amount Range": amount_range,
        "Status": status
    }
    results.append(result)

    async with tasks_lock:
        with open(RESULT, "a", encoding="utf-8") as f:
            f.write(f"{result['Address']} | {result['Amount Range']} | {result['Status']}\n")


async def parse_info(semaphore, address, proxy):
    async with semaphore:
        for attempt in range(1, NUMBER_OF_ATTEMPTS + 1):
            try:
                logger.info(f'{address} | попытка {attempt}/{NUMBER_OF_ATTEMPTS}')
                async with BaseAsyncSession(proxy=proxy, verify=False) as async_session:
                    headers = {
                        'accept': '*/*',
                        'accept-language': 'en-US,en;q=0.9',
                        'content-type': 'application/json',
                        'referer': 'https://claim.elixir.xyz/',
                        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
                    }
                    params = {'address': address}
                    
                    response = await async_session.get('https://claim.elixir.xyz/backend/wallet/eligibility', params=params, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        eligibility = data.get("eligibility", False)
                        amount_range = data.get("tokenAmountRange", {})
                        amount_start = float(amount_range.get("amountStart", "0"))
                        amount_end = float(amount_range.get("amountEnd", "0"))
                        
                        if not eligibility:
                            await save_result(address, 0, 0, "Not Eligible")
                        else:
                            await save_result(address, amount_start, amount_end)

                        logger.info(f'{address} | Eligibility: {eligibility} | Amount Range: {amount_start} - {amount_end}')
                        return  
                    else:
                        logger.error(f'{address} | Код ответа: {response.status_code} | Текст: {response.text}')
            except Exception as e:
                logger.error(f'{address} | Ошибка: {e}')
        
        failure_text = f'{address} | Не удалось спарсить после {NUMBER_OF_ATTEMPTS} попыток'
        logger.error(failure_text)
        await save_result(address, None, None, "Parsing Failed")

async def main():
    evm_addresses = get_info(EVM_ADDRESSES)
    proxies = get_info(PROXIES)
    if not evm_addresses:
        logger.error(f'Нет адресов в {EVM_ADDRESSES}.')
        return
    if len(proxies) < len(evm_addresses):
        logger.error(f'Кол-во прокси меньше, чем адресов. Прокси: {len(proxies)} | Адресов: {len(evm_addresses)}')
        return
    
    semaphore = asyncio.Semaphore(ASYNC_TASK_IN_SAME_TIME)
    tasks = [asyncio.create_task(parse_info(semaphore, address, proxies[num])) for num, address in enumerate(evm_addresses)]
    await asyncio.gather(*tasks)
    
    df = pd.DataFrame(results)
    successful_entries = df[df["Status"].str.startswith("✅ Success")]

    if not successful_entries.empty:
        min_total = successful_entries["Amount Range"].apply(lambda x: float(x.split(" - ")[0]) if " - " in x else 0).sum()
        max_total = successful_entries["Amount Range"].apply(lambda x: float(x.split(" - ")[1]) if " - " in x else 0).sum()
    else:
        min_total, max_total = 0, 0

    logger.info("\n✅ Все задачи завершены! Результаты записаны в файл.")
    logger.info("\nРезультаты:")
    logger.info("\n" + tabulate(df, headers="keys", tablefmt="grid"))
    logger.info(f"\nОбщая сумма ELX (Range): {min_total:.8f} - {max_total:.8f}")

    # Подсчет статистики по кошелькам
    total_wallets = len(df)
    eligible_wallets = df[df["Status"] == "✅ Success: Eligible"].shape[0]
    not_eligible_wallets = df[df["Status"] == "❌ Success: Not Eligible"].shape[0]
    failed_wallets = df[df["Status"].str.startswith("❌ Error")].shape[0]

    logger.info("\n📊 Статистика по кошелькам:")
    logger.info(f"Всего кошельков: {total_wallets}")
    logger.info(f"✅ Eligible: {eligible_wallets}")
    logger.info(f"❌ Not Eligible: {not_eligible_wallets}")
    logger.info(f"⚠️ Не спарсилось: {failed_wallets}")


if __name__ == "__main__":
    asyncio.run(main())
