# -*- coding: utf-8 -*-
from datetime import datetime
from collections import defaultdict

from twisted.logger import Logger
from twisted.internet import threads
from twisted.internet.defer import inlineCallbacks, returnValue

from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra.util import uuid_from_time
from cassandra import InvalidRequest, AlreadyExists


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
    log = Logger()
    _connection = None
    _session = None

    def __init__(self, hosts=None, keyspace=None, **kwargs):
        """
        :param hosts: A list of Casssandra nodes. Defaults to localhost.
        :param keyspace: A default keyspace.
        """
        self.hosts = hosts or ["localhost"]
        self.keyspace = keyspace

        CassandraHistory._connection = Cluster(self.hosts)
        CassandraHistory._session = self._connection.connect()
        self.session.row_factory = dict_factory

        self.set_keyspace(self.keyspace, kwargs.get('create_keyspace', True))
        self._create_schema()

    def execute(self, query, query_args=None):
        """Executes a query in a blocking fashion. Use `execute_async` if you are
        using Twisted (and you probably are!)

        :param query: The query string.
        :param query_args: A tuple or list of query arguments, if needed.
        :returns: a `cassandra.Cluster.ResultSet` object.
        """
        return self.session.execute(query, query_args)

    @inlineCallbacks
    def execute_async(self, query, query_args=None):
        """Executes query in a thread so it won`t block the main thread.

        :param query: The query string.
        :param query_args: A tuple or list of query arguments, if needed.
        :returns: a `cassandra.Cluster.ResultSet` object.
        """
        result = yield threads.deferToThread(self.execute, query, query_args)
        returnValue(result)

    @property
    def session(self):
        return CassandraHistory._session

    def set_keyspace(self, keyspace, create_if_needed):
        """
        """
        try:
            self.session.set_keyspace(keyspace)
        except InvalidRequest:
            if create_if_needed:
                self._create_keyspace(keyspace)
                self.session.set_keyspace(keyspace)

    def _create_keyspace(self, keyspace, replication_class='SimpleStrategy',
                         replication_factor=3):
        """Creates a keyspace.

        :param keyspace: The keyspace to be created. The keyspace is like
        a schema, a container for the tables where you set also properties
        on replication and consistency.
        :param replication_class: Defaults to 'SimpleStrategy' (first replica
        placement strategy).
        :param replication_factor: Defaults to 3.
        """
        return self.execute(
            "CREATE KEYSPACE {} WITH replication = "
            "{{'class': '{}', 'replication_factor': {}}}".format(
                keyspace, replication_class, replication_factor))

    def _create_schema(self):
        query = """
            CREATE TABLE room_history (
                room_id varchar,
                message_id timeuuid,
                author varchar,
                message varchar,
                PRIMARY KEY ((room_id), message_id))
            WITH CLUSTERING ORDER BY (message_id DESC)
        """
        try:
            self.execute(query)
            self.log.info('Cassandra Room History table created.')
        except AlreadyExists:
            self.log.info('Cassandra Room History table already created.')

    @inlineCallbacks
    def save(self, channel_id, author, message):
        """Saves the history into an in-memory structure.

        :param channel_id: The channel_id.
        :param author: The author name.
        :param message: The message itself.
        """
        query = """
            INSERT INTO
                room_history (room_id, message_id, author, message)
            VALUES (%s, %s, %s, %s)
        """

        message_id = uuid_from_time(datetime.now())
        yield self.execute(query, (channel_id, message_id, author, message))

    @inlineCallbacks
    def get(self, channel_id, lines=100, offset=0):
        """Get batches of old messages stored in the history.

        :param channel_id: The channel_id.
        :param lines: How many lines to retrieve, defaults to 100.
        :param offset: Defaults to 0, works similarly as SQL Offset.
        """
        query = """
            SELECT author, message FROM room_history
            WHERE room_id = %s
            LIMIT {}
        """.format(lines)
        result = yield self.execute_async(query, (str(channel_id), ))

        result = list(reversed(list(result)))  # argh
        returnValue(result)
