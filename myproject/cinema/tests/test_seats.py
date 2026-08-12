from django.test import SimpleTestCase

from cinema.seats import generate_seats, is_valid_seat


class SeatHelperTestCase(SimpleTestCase):
    def test_generate_and_validate_seats(self):
        self.assertEqual(generate_seats(1), ["A1"])
        self.assertEqual(generate_seats(11)[-1], "B1")
        self.assertTrue(is_valid_seat("A1", 50))
        self.assertFalse(is_valid_seat("Z99", 50))
        with self.assertRaises(ValueError):
            generate_seats(0)
