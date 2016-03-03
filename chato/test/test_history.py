from twisted.trial.unittest import TestCase

from chato.history import MemoryHistory


class TestMemoryHistory(TestCase):
    def setUp(self):
        self.history = MemoryHistory()

    def tearDown(self):
        self.history.clear()

    def test_save_empty_author_raises_error(self):
        self.assertRaises(ValueError, self.history.save, 1, None, 'MEssage!')

    def test_save_empty_message_raises_error(self):
        self.assertRaises(ValueError, self.history.save, 1, 'YEAH', '')

    def test_save_empty_raises_error(self):
        self.assertRaises(ValueError, self.history.save, 1, None, '')

    def test_save_no_channel_raises_error(self):
        self.assertRaises(ValueError, self.history.save, '', 'Author', 'MSG')

    def test_save_once_new_room(self):
        self.history.save(1, 'Nicholas', 'Yo Brows')

        data = self.history.get(1)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0], {'author': 'Nicholas', 'message': 'Yo Brows'})

    def test_save_multiple_rooms(self):
        self.history.save(1, 'Nicholas', 'Yo Brows')
        self.history.save(2, 'Doo Wop', 'I came running')
        self.history.save('room3', 'Stevie Wonder', 'Baby I just cant see')
        self.history.save('room3', 'Lindsay', 'Please dont go...')

        data = self.history.get(1)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0], {'author': 'Nicholas', 'message': 'Yo Brows'})

        data = self.history.get('room3')
        self.assertEqual(len(data), 2)

        # Oldest ones should be first
        self.assertEqual(
            data[0],
            {'author': 'Stevie Wonder', 'message': 'Baby I just cant see'})

        self.assertEqual(
            data[1],
            {'author': 'Lindsay', 'message': 'Please dont go...'})

    def test_clear(self):
        self.history.save(1, 'Nicholas', 'Yo Brows')

        data = self.history.get(1)
        self.assertEqual(len(data), 1)

        self.history.clear()
        data = self.history.get(1)
        self.assertEqual(len(data), 0)
