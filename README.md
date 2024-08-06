# python-eventemitter
![Build status](https://github.com/jonghwanhyeon/python-eventemitter/actions/workflows/publish.yml/badge.svg)

A Python port of Node.js EventEmitter that supports both synchronous and asynchronous event execution

## Help
See [documentation](https://python-eventemitter.readthedocs.io) for more details

## Install
To install **python-eventemitter**, simply use pip:

```console
$ pip install python-eventemitter
```

## Usage
### Synchronous API
```python
from eventemitter import EventEmitter


def main():
    ee = EventEmitter()

    sounds: list[str] = []

    ee.add_listener("sound", lambda: sounds.append("woof"))
    ee.prepend_listener("sound", lambda: sounds.append("meow"))
    ee.on("sound", lambda: sounds.append("oink"))

    @ee.on("sound")
    def from_cow():
        sounds.append("moo")

    @ee.once("sound")
    def from_bee():
        sounds.append("buzz")

    ee.emit("sound")  # Run events in order
    print(sounds)  # ['meow', 'woof', 'oink', 'moo', 'buzz']


if __name__ == "__main__":
    main()
```

### Asynchronous API
``` python
import asyncio

from eventemitter import AsyncIOEventEmitter


async def main():
    aee = AsyncIOEventEmitter()

    sounds: set[str] = set()

    aee.add_listener("sound", lambda: sounds.add("woof"))
    aee.prepend_listener("sound", lambda: sounds.add("meow"))
    aee.on("sound", lambda: sounds.add("oink"))

    @aee.on("sound")
    def from_cow():
        sounds.add("moo")

    @aee.once("sound")
    async def from_bee():
        sounds.add("buzz")

    await aee.emit("sound") # Run events concurrently
    print(sounds)  # {'woof', 'meow', 'buzz', 'moo', 'oink'}


if __name__ == "__main__":
    asyncio.run(main())
```