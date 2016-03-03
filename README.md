## Chat-O ##

This project is an __alpha__ attempt at helping anyone implement a chat service/client in your own server and website.

For now, we are only providing a server (implemented using [Crossbar](http://crossbar.io)) and a demo client that you can access under `http://localhost:9166`.

#### Features ####

- Send and Receive messages
- Chat Room support
- History. Two backends: In-Memory and Cassandra.
- Custom Django templatetag to insert a chat client widget in your site.


### How to Install and Run the Server (Crossbar) ###

This assumes you have virtualenv.


```bash
$ git clone https://github.com/nicholasamorim/chato.git
$ mkvirtualenv chato; cd chato
$ pip install -r requirements.txt
$ ./run
```

This starts a Crossbar server and you can test it pointing your browser at `http://localhost:9166` for a very ugly and basic implementation of a server.


### Using Client in a Django (alpha) ###

1. Add chato.utils.django' to your `INSTALLED_APPS`.
2. Go into your template and do:

```html
{% load chato_client %}
{% chato_widget %}
```

This will add the Chat-O widget to your page and should work right away.

The template tag accepts two arguments: include_css and include_jquery. They both default to True.

#### Tests ####

If you wanna run the tests:

```bash
$ ./run_tests
```


### Roadmap ###

- Refactor Django code.
- Add django management command to start Crossbar server.
- Create proper encapsulated CSS.
- Add flexibility through configuration flags and settings variables.
- Presence indicator (user went online, offline)
- More tests.