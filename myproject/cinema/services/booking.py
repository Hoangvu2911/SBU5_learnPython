from cinema.services.seat_map import SeatMapBuilder
from cinema.services.commands import BookingCommand, PayTicketCommand, CancelTicketCommand

class BookingFacade:
    def get_seat_map(self, showtime):
        return (
            SeatMapBuilder(showtime)
            .with_cleanup()
            .with_booked_seats()
            .with_held_seats()
            .build()
        )

    def book_seat(self, user, showtime, seat: str):
        return BookingCommand(user, showtime, seat).execute()

    def pay_ticket(self, user, ticket):
        return PayTicketCommand(user, ticket).execute()

    def cancel_ticket(self, user, ticket):
        return CancelTicketCommand(user, ticket).execute()