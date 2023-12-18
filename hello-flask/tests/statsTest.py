import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
import sys
sys.path.insert(0, '../')
from stats import count_unique_words, preload_data, update_data
import sqlite3

class TestCalculateTdidf(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.cursor = MagicMock()
        self.ctx = MagicMock()  # Mock the context object
        self.ctx.send = AsyncMock()  # Mock the send method with AsyncMock
        self.db.cursor.return_value = self.cursor

    @patch('sqlite3.connect')
    def test_calculate_tdidf(self, mock_connect):
        mock_connect.return_value = self.db

        async def async_test():
            expected_output = ["dragonfruit", "cherry"]

            # Mock the execute method to not do anything
            self.cursor.execute = MagicMock()

            # Mock the fetchall method to return your test data
            self.cursor.fetchall.return_value = [
                ("user1", "guild1", "apple banana cherry"),
                ("user1", "guild1", "banana cherry dragonfruit"),
                ("user2", "guild1", "apple banana eggplant"),
                ("user2", "guild1", "banana eggplant fig"),
            ]

            output = await count_unique_words(self.ctx, "user1", "guild1")

            self.assertEqual(output, expected_output)
            print(f'Output for user1: {output}')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_test())
        loop.close()

     
