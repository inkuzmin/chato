## Chat-O ##

This project is an __alpha__ attempt at helping anyone implement a chat service/client in your own server and website.

For now, we are only providing a server (implemented using [Crossbar](http://crossbar.io)) and a demo client that you can access under `http://localhost:8080`.

Soon, we'll be adding generic chat clientes in HTML + CSS and helpers to add it to frameworks like Django.

#### Features ####

- Send and Receive messages
- Chat Room support
- History retrieval (in-memory only, storage support to be added)


### How to Install and Run the Server (Crossbar) ###

This assumes you have virtualenv.


```bash
$ git clone https://github.com/nicholasamorim/chato.git
$ mkvirtualenv chato; cd chato
$ pip install -r requirements.txt
$ ./run
```

This starts a Crossbar server and you can test it pointing your browser at `http://localhost:8080` for a very ugly and basic implementation of a server.

#### Tests ####

If you wanna run the tests:

```bash
$ ./run_tests
```
