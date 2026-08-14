from decimal import Decimal
from datetime import datetime
from abc import ABC, abstractmethod

class PriceComponent(ABC):
    @abstractmethod
    def get_price(self) -> Decimal:
        pass
    
class BasePrice(PriceComponent):
    def __init__(self, amount: Decimal):
        self._amount = Decimal(amount)

    def get_price(self) -> Decimal:
        return self._amount

class PriceDecorator(PriceComponent):
    def __init__(self, inner: PriceComponent):
        self._inner = inner
    
    def get_price(self) -> Decimal:
        return self._inner.get_price()

class WeekendPriceDecorator(PriceDecorator):
    def __init__(self, inner: PriceComponent, start_at: datetime):
        super().__init__(inner)
        self._start_at = start_at

    def get_price(self) -> Decimal:
        price = self._inner.get_price()
        if self._start_at.weekday() >= 5:
            return (price * Decimal('1.10')).quantize(Decimal('0.01'))
        return price

class PromoPriceDecorator(PriceDecorator):
    def __init__(self, inner: PriceComponent, discount: Decimal):
        super().__init__(inner)
        self._discount = discount

    def get_price(self) -> Decimal:
        return max(Decimal('0.00'), self._inner.get_price() - self._discount)

def build_ticket_weekend_price(showtime, enable_weekend: bool = False) -> Decimal:
    price: PriceComponent = BasePrice(showtime.base_price)
    if enable_weekend:
        price = WeekendPriceDecorator(price, showtime.start_at)
    return price.get_price()

def build_build_ticket_discount_price(showtime, discount: Decimal | None = None) -> Decimal:
    price: PriceComponent = BasePrice(showtime.base_price)
    if discount:
        price = PromoPriceDecorator(price, discount)
    return price.get_price()

def build_ticket_price(showtime, enable_weekend: bool = False, discount: Decimal | None = None) -> Decimal:
    price: PriceComponent = BasePrice(showtime.base_price)
    if discount is not None and discount > Decimal('0.00'):
        price = PromoPriceDecorator(price, discount)
    if enable_weekend:
        price = WeekendPriceDecorator(price, showtime.start_at)
    return price.get_price() 