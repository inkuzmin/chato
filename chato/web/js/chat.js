"use strict";


var channelID = "ch1",
    currentSubscription = null,
    presetNicks = ["Nick", "Knatterton", "Micky", "Maus", "Donald", "Bruce", "Wayne", "Clark", "Kent", "Sarah", "Connor", "Mary", "Shelley", "Rosemary", "Wilma", "Louis", "Selina", "Barbara", "Gordon", "Herbert", "The Count"],
    nick,
    oldNick,
    assignedNicks = {},
    nickColors = ["black", "orange", "green", "blue", "red"],
    sess = null,
    retryCount = 0,
    retryDelay = 2,
    isReconnect = false;

var chatWindow = null;

setupDemo();
connect();


function subscribeChannel(channelID) {
   if (currentSubscription === null) {
      sess.subscribe(channelID, onMessage).then(
         function(subscription) {
            console.log("Successfully subscribed channel " + channelID);
            currentSubscription = subscription;
         },
         function(error) {
            console.log("Subscription error ", error);
         }
      );
   }

   // clear messages box
   $("#messages_box").html('');
   // // set the second instance link
   // $('#secondInstance').attr('href', window.location.pathname + '#' + newChannelID);
   // clear the unread chat message indicator if set
   $("#show_chat_window").removeClass("message_received");
}

function connect() {

   var wsuri;
   wsuri = "ws://127.0.0.1:9166/ws";
   var connection = new autobahn.Connection({
      url: wsuri,
      realm: "coffee"
   });

   connection.onopen = function (session, details) {
      sess = session;

      console.log("Connected! Is Reconnect:" + isReconnect);
      console.log("Attempting to subscribe channel ", channelID);

      if (!isReconnect) {
         subscribeChannel(channelID);
         changeChannelIndicators(channelID);
         getHistory(channelID)
         isReconnect = true;
      }

   };

   connection.onclose = function(reason, details) {
      sess = null;
      console.log("connection closed ", reason, details);
   }

   connection.open();

}


function changeChannelIndicators ( newChannelID ) {
   // set the channel title on the chat window
   $("#channel_title").text("Channel " + newChannelID);
}


function setupDemo() {
   chatWindow = $("#chat_window");

   // initial timed display of the chat window
   // window.setTimeout(function() { $("#chat_window").toggle(300) }, 2300);

   // set up show + hide chat window handlers
   document.getElementById("show_chat_window").onclick = function () {

      $("#chat_window").toggle(300);

      var messagesBox = $("#messages_box")[0];

      // scroll messages box
      messagesBox.scrollTop = messagesBox.scrollHeight;

   };

   document.getElementById("hide_chat_window").onclick = function () {

      $("#chat_window").toggle(300);
      $("#show_chat_window").removeClass("message_received");

   };


   // set random preset nick
   nick = $("#nick");
   var randomNick = presetNicks[Math.floor(Math.random() * presetNicks.length)];
   nick.val(randomNick);
   oldNick = nick.val();
   getNickColor(nick.val()); // assigns a color to the nick

   // set 'enter' on chat message textarea sends message
   var messageInput = $("#message_input")[0];
   messageInput.onkeypress = function(e) {

      var e = e || event; // IE8 fix, since here the window.event, not the event itself contains the keyCode

      if (e.keyCode === 13) {

         console.log("enter");
         sendMessage(messageInput);

         return false;

      };

   };
}

function sendMessage(messageInput) {
   console.log("send message");

   var message = messageInput.value;
   var currentNick = nick.val();

   var payload = {};
   payload.type = "message";
   payload.message = message;
   payload.author = currentNick;
   payload.channel = channelID;

   sess.call('message.send', [payload])

   // clear the message input
   messageInput.value = '';
   messageInput.placeholder = '';

};

/**
 * Retrieves history for given channel and calls
 * {@link addMessage} for every message in the history.
 * @function
 * @param {string} channelID
 * @return undefined
 */
function getHistory(channelID) {
   console.log("Retrieving history for channel " + channelID);

   sess.call('history.get', [channelID]).then(
      function(data, kwargs, detail) {
         if (data) {
            $.map(data, addMessage);
         }
      },
      function(error) {
         console.log('Error retrieving history');
      }
   )
}

function changeOwnNick(currentNick) {

   // get the color value for the old nick
   var nickColor = assignedNicks[oldNick];

   // delete the old nick
   delete assignedNicks[oldNick];

   // add new nick with the old color
   assignedNicks[currentNick] = nickColor;

};


function getNickColor(nickString) {

   // check if nickstring has color assigned, and return this
   if (!(nickString in assignedNicks)) {

      // count the nicks
      var nickCounter = 0;
      for (var i in assignedNicks) {
         if (assignedNicks.hasOwnProperty(i)) {
            nickCounter += 1;
         }
      }

      // pick a color
      var nickColor;
      if (nickCounter <= nickColors.length) {
         nickColor = nickColors[nickCounter];
      }
      else {
         nickColor = nickColors[(nickCounter % nickColors.length)];
      }

      // add the nick and color
      assignedNicks[nickString] = nickColor;

   }

   return assignedNicks[nickString];

};

function onMessage(args, kwargs, details) {
   console.log("onMessage");
   var payload = args[0];
   addMessage(payload);
   // set new message highlighting on "chat" button
   $("#show_chat_window").addClass("message_received");

}

/**
 * Adds message to the chat window.
 * @function
 * @param {Object} a message Object containing keys like
 * message and author.
 * @return undefined
 */
function addMessage(payload) {
   // get the parts of the message event
   var message = payload.message;
   var messageNick = payload.author;
   var nickColor = getNickColor(messageNick);

   var messageTime = formattedMessageTime();

   var messagesBox = $("#messages_box")[0];

   // add html to messages box
   $(messagesBox).append("<p class='nick_line' style='color: " + nickColor + ";'>" + messageNick + " - <span class='message_time'>" + messageTime + "</span></p>");
   $(messagesBox).append("<p class='message_line'>" + message + "</p>");
   $(messagesBox).append("</br>");

   // scroll messages box
   messagesBox.scrollTop = messagesBox.scrollHeight;

}

function formattedMessageTime() {

   var messageTimeRaw = new Date();

   var day = messageTimeRaw.getDate();
   var month = messageTimeRaw.getMonth() + 1;
   var hours = messageTimeRaw.getHours();
   var minutes = messageTimeRaw.getMinutes();
   // add initial '0' where necessary
   minutes = minutes < 10 ? "0" + minutes : minutes;
   hours = hours < 10 ? "0" + hours : hours;

   var formattedMessageTime = hours + ":" + minutes;
   return formattedMessageTime;
};
