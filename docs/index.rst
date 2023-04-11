Welcome to python-eventemitter's documentation!
===============================================

**python-eventemitter** is a Python port of Node.js EventEmitter

Install
-------

To install **python-eventemitter**, simply use pip:

.. code-block:: console

   $ pip install python-eventemitter

Example
-------

Synchronous API
^^^^^^^^^^^^^^^

.. code-block:: python

   from eventemitter import EventEmitter

   ee = EventEmitter()

   @ee.on("connected")
   def on_connected():
      print("connected")

   @ee.on("message")
   def on_message(message: str):
      print(f"received: {message}")

   ee.emit("connected")
   ee.emit("message", "message from client")

Asynchronous API
^^^^^^^^^^^^^^^^

.. code-block:: python

   import asyncio
   from eventemitter.asyncio import AsyncIOEventEmitter

   ee = AsyncIOEventEmitter()

   @ee.on("connected")
   def on_connected():
      print("connected")

   @ee.on("message")
   async def on_message(message: str):
      await asyncio.sleep(0.1)
      print(f"received: {message}")

   ee.emit("connected")
   ee.emit("message", "message from client")


Contents
---------
.. toctree::
   :maxdepth: 2

   api/index