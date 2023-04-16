# eat-paste

> Miss Hoover: Now put paste on your paper. Ralph, are you eating your paste? <br/>
> Ralph Wiggum: (Gluestick poking out of his mouth) No, Miss. Hoover.

This is a simple paste server. There is no authentication, you simply send a text/plain post to /paste on the server and get back a slug. The text that was posted will then be available at that slug.

Note that the paste server won't accept anything that the Python Bleach library doesn't like.

It uses a MongoDB database as the backend.

## Usage

```
$ echo "hi there you super cool paste thing" | \
curl -H "Content-Type: text/plain" -X POST --data-binary @- http://localhost:5000/paste
savvy-caracal
```

Now curl that paste.

```
$ curl localhost:5000/paste/savvy-caracal
hi there you super cool paste thing
```

## MongoDB

The application expects a MONGO_CONNECTION string. That could be a simple MongoDB Altas shared database.

## Curl Examples

Send a file:

```
curl -d "@data.txt"  -H "Content-Type: text/plain" -X POST http://localhost:5000/paste
```

Echo some text:

```
echo "hi there" | curl -H "Content-Type: text/plain" -X POST --data-binary @- http://localhost:5000
```