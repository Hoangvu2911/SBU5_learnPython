import logging
from typing import Protocol

logger = logging.getLogger(__name__)

class TicketObserver(Protocol):
    def update(self, event: str, ticket) -> None:
        pass

class LoggingObserver:
    def update(self, event: str, ticket) -> None:
        logger.info(f"Event: {event}, Ticket: {ticket.id}, status: {ticket.status}")

class AuditObserver:
    def __init__(self):
        self.events: list[tuple] = []

    def update(self, event: str, ticket) -> None:
        self.events.append((event, ticket.id, ticket.status))

class TicketEventPublisher:
    def __init__(self):
        self._observers: list[TicketObserver] = []
    
    def subscribe(self, observer: TicketObserver) -> None:
        self._observers.append(observer)

    def notify(self, event: str, ticket) -> None:
        for observer in self._observers:
            observer.update(event, ticket)

ticket_events = TicketEventPublisher()
ticket_events.subscribe(LoggingObserver())