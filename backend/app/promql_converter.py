import re

class PromQLConverter:
    def __init__(self, metric_name: str = "moex_share_price"):
        # Имя базовой метрики в VictoriaMetrics (например, цена акций)
        self.metric_name = metric_name
        # Регулярка разрешает только: тикеры (A-Z), числа (0-9), точки, скобки и знаки + - * /
        self.safe_pattern = re.compile(r'^[A-Z0-9.+\-*/()\s]+$')

    def convert(self, user_formula: str) -> str:
        """
        Превращает пользовательскую формулу вроде "(SBER * 2) / GAZP"
        в PromQL: "(moex_share_price{ticker='SBER'} * 2) / moex_share_price{ticker='GAZP'}"
        """
        # 1. Очищаем от лишних пробелов и приводим к верхнему регистру
        cleaned_formula = user_formula.strip().upper()

        if not cleaned_formula:
            raise ValueError("Формула не может быть пустой")

        # 2. Жесткая валидация на безопасность (блокируем инъекции)
        if not self.safe_pattern.match(cleaned_formula):
            raise ValueError(
                "Обнаружены запрещенные символы! "
                "Разрешены только тикеры (латиница), числа и знаки +, -, *, /, (, )"
            )

        # 3. Магия трансляции: находим все отдельные слова (тикеры) и заменяем их на PromQL-метрики
        # Исключаем числа (например, чтобы '2' или '1.5' не превратились в тикеры)
        def replace_ticker(match):
            token = match.group(0)
            # Если это число (целое или с плавающей точкой) — оставляем как есть
            if re.match(r'^\d+(\.\d+)?$', token):
                return token
            # Если это слово (тикер) — оборачиваем в формат VictoriaMetrics
            return f'{self.metric_name}{{ticker="{token}"}}'

        # Выделяем токены (слова или числа)
        promql_expr = re.sub(r'[A-Z0-9.]+', replace_ticker, cleaned_formula)

        return promql_expr
