import asyncio
import logging
import time
import aiohttp
import aiomoex
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MoexWorker")

# Список тикеров для MVP
TICKERS_TO_TRACK = ["SBER", "GAZP", "LKOH", "YNDX", "ROSN", "NVTK", "VTBR", "T"]

async def fetch_and_format_marketdata(session: aiohttp.ClientSession) -> str:
    """
    Запрашивает живые рыночные данные режима TQBR через aiomoex.
    Формирует строгий синтаксис Influx Line Protocol.
    """
    columns = ("SECID", "LAST", "VOLUME")
    
    data = await aiomoex.get_board_securities(
        session,
        board="TQBR",
        market="shares",
        table="marketdata",
        columns=columns
    )
    
    if not data:
        return ""
        
    lines = []
    # VictoriaMetrics отлично понимает миллисекунды, сделаем таймстамп стабильным
    current_ms = int(time.time() * 1000) 
    
    for row in data:
        ticker = row.get("SECID")
        price = row.get("LAST")
        volume = row.get("VOLUME")
        
        # Жесткая проверка: тикер в списке, цена существует и она выше нуля
        if ticker in TICKERS_TO_TRACK and price is not None:
            try:
                price_f = float(price)
                if price_f <= 0:
                    continue
                    
                # Формируем строку строго по спецификации: moex_share_price,ticker=SBER value=265.40 1672531199000
                lines.append(f"moex_share_price,ticker={ticker} value={price_f} {current_ms}")
                
                if volume is not None:
                    volume_f = float(volume)
                    lines.append(f"moex_share_volume,ticker={ticker} value={volume_f} {current_ms}")
            except (ValueError, TypeError):
                # Если Мосбиржа прислала битые данные (строку вместо числа) — просто пропускаем
                continue
                
    return "\n".join(lines)

async def push_to_victoria_metrics(payload: str):
    """Пушит сформированные метрики в стандартный эндпоинт /write."""
    if not payload:
        return
        
    # Использовать /write — это самый надежный и прямой путь для single-node VictoriaMetrics
    vm_url = "http://victoria-metrics:8428/write"
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # Передаем payload как обычную строку текста (content)
            response = await client.post(vm_url, content=payload)
            if response.status_code in (204, 200):
                logger.info("Данные через aiomoex успешно уложены в VictoriaMetrics.")
            else:
                logger.error(f"VM вернула ошибку {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Не удалось отправить данные в СУБД: {e}")

async def moex_worker_loop():
    logger.info("Запуск фонового воркера на базе aiomoex...")
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                influx_payload = await fetch_and_format_marketdata(session)
                if influx_payload:
                    await push_to_victoria_metrics(influx_payload)
                else:
                    logger.warning("Нет данных от MOEX для текущего среза тикеров.")
            except Exception as e:
                logger.error(f"Критический сбой в цикле aiomoex-воркера: {e}")
                
            await asyncio.sleep(30)
