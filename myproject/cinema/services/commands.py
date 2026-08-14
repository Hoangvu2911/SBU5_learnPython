from abc import ABC, abstractmethod
import logging

from cinema import booking as legacy
from cinema.services.events import ticket_events

logger = logging.getLogger(__name__)


class TicketActionCommand(ABC):

    def execute(self):
        try:
            ticket = self._do_action()
            self._after_success(ticket)
            return ticket
        except Exception as e:
            self._after_failure(e)
            raise

    @abstractmethod
    def _do_action(self):
        pass

    @abstractmethod
    def _success_event(self) -> str:
        pass

    def _failure_event(self) -> str:
        return f"{self._success_event()} failed"

    def _after_success(self, ticket) -> None:
        ticket_events.notify(self._success_event(), ticket)

    def _after_failure(self, error: Exception) -> None:
        logger.error("Error %s: %s", self._failure_event(), error)


class BookingCommand(TicketActionCommand):
    def __init__(self, user, showtime, seat: str):
        self.user = user
        self.showtime = showtime
        self.seat = seat

    def _do_action(self):
        return legacy.book(self.user, self.showtime, self.seat)

    def _success_event(self) -> str:
        return "booked"


class PayTicketCommand(TicketActionCommand):
    def __init__(self, user, ticket):
        self.user = user
        self.ticket = ticket

    def _do_action(self):
        return legacy.pay(self.user, self.ticket)

    def _success_event(self) -> str:
        return "paid"


class CancelTicketCommand(TicketActionCommand):
    def __init__(self, user, ticket):
        self.user = user
        self.ticket = ticket

    def _do_action(self):
        return legacy.cancel_ticket(self.user, self.ticket)

    def _success_event(self) -> str:
        return "cancelled"
