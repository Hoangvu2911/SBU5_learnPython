export interface Movie {
    id: number;
    title: string;
    description: string;
    release_date: string;
    genre: string;
    rating: number;
    duration_minutes: number;
    director: string;
    is_active: boolean;
    cast: { id: number; name: string }[];
}

export interface Paginated<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export type SeatStatus =  "available" | "held" | "booked";

export interface Seat {
  seat: string;
  status: SeatStatus;
}

export type ShowtimeStatus = "scheduled" | "ongoing" | "cancelled" | "completed";

export interface Showtime {
    id: number;
    movie: number;
    movie_title: string;
    room: number;
    room_name: string;
    start_at: string;
    end_at: string;
    base_price: string;
    status: ShowtimeStatus;
    is_bookable: boolean;
}

export interface SeatMapResponse {
    showtime: Showtime;
    seats: Seat[];
}

export type TicketStatus = "pending" | "booked" | "cancelled";

export interface AuthUser {
    id: number;
    username: string;
    is_staff: boolean;
}

export interface AuthResponse {
    token: string;
    user: AuthUser;
}

