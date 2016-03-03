# -*- coding: utf-8 -*-
from collections import defaultdict


class History(object):
    """A base class that defines an interface to implement
    chat history.
    """
    def save(self, channel_id, author, message):
        """Should save a line of history somewhere."""
        raise NotImplementedError

    def get(self, channel_id, lines=100, offset=0):
        """Should retrieve `lines` amount with a specified `offset`."""
        raise NotImplementedError


class MemoryHistory(History):
    """In-Memory history. Used for tests.

    .. warning:: History will be wiped out on every application
    shutdown.

    .. warning:: No care is being taken on history memory size.
    """
    _history = defaultdict(list)

    def save(self, channel_id, author, message):
        """Saves the history into an in-memory structure.

        :param channel_id: The channel_id.
        :param author: The author name.
        :param message: The message itself.
        """
        if not channel_id:
            raise ValueError('Channel ID is empty')

        if not author:
            raise ValueError('Author is empty')

        if not message:
            raise ValueError('Message is empty')

        MemoryHistory._history[channel_id].append({
            'author': author,
            'message': message})

    def get(self, channel_id, lines=100, offset=0):
        """Get batches of old messages stored in the history.

        :param channel_id: The channel_id.
        :param lines: How many lines to retrieve, defaults to 100.
        :param offset: Defaults to 0, works similarly as SQL Offset.
        """
        if channel_id not in MemoryHistory._history:
            return []

        return MemoryHistory._history[channel_id][offset:(lines + offset)]

    def __str__(self):
        """Returns first 1000 characters of history data structure.
        """
        return str(MemoryHistory._history)[:1000]

    def clear(self):
        """Clears the history. Used for test purposes.
        """
        MemoryHistory._history = defaultdict(list)


class CassandraHistory(object):
    """History storage and retrieval on
    `Cassandra <http://cassandra.apache.org/>`_ database in a non-blocking
    fashion.
    """
    def save(self, channel_id, author, message):
        """Saves the history into an in-memory structure.

        :param channel_id: The channel_id.
        :param author: The author name.
        :param message: The message itself.
        """
        # query = """INSERT INTO
        #     chat_history (channel_id, author, message)
        #     VALUES (%s, %s, %s)
        # """
        raise NotImplementedError

    def get(self, channel_id, lines=100, offset=0):
        """Get batches of old messages stored in the history.

        :param channel_id: The channel_id.
        :param lines: How many lines to retrieve, defaults to 100.
        :param offset: Defaults to 0, works similarly as SQL Offset.
        """
        raise NotImplementedError
