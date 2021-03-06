# -*- coding: utf-8 -*-
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.logger import Logger

from autobahn.twisted.wamp import ApplicationSession

from history import CassandraHistory

history = CassandraHistory(["localhost"], "chato")


class AppSession(ApplicationSession):
    log = Logger()

    def _save_to_history(self, payload):
        """Implements a (very) fragile history saving mechanism as of now.

        :param payload: The original `sendMessage` payload.
        """
        history.save(
            payload['channel'],
            payload['author'],
            payload['message'])

        self.log.debug('History: {}'.format(history))

    @inlineCallbacks
    def getHistory(self, channel_id, lines=80, offset=0):
        """Gets `lines` of history.

        :param channel_id: The channel_id.
        :param lines: How many lines to retrieve, defaults to 100.
        :param offset: Defaults to 0, works similarly as SQL Offset.
        """
        data = yield history.get(channel_id, lines, offset)
        returnValue(data)

    @inlineCallbacks
    def sendMessage(self, payload):
        """Publishes message contained in `payload`.

        Registered as a RPC method. Encapsulates history.

        :param payload: The payload sent by session.call. This argument
        must contain:
            - channel
            - author
            - message
            - timestamp (UTC unix timestamp)
        """
        self.log.info('Call to sendMessage: {payload}', payload=payload)
        self._save_to_history(payload)
        yield self.publish(payload['channel'], payload)

    @inlineCallbacks
    def onJoin(self, details):
        """Called when a Worker joins the application.

        It simply register RPC calls for now,
        """
        self.log.info('A new session...')
        yield self.register(self.sendMessage, 'message.send')
        yield self.register(self.getHistory, 'history.get')
