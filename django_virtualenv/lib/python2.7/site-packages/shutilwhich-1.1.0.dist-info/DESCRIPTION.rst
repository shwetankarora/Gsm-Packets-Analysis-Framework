A copy & paste backport of Python 3.3's ``shutil.which`` function.

Usage
=====

First, install the package: ``pip install shutilwhich``

Importing the package::

  import shutilwhich

will monkey-patch the ``shutil`` package, so from that point on you can simply
import the ``which`` function::

  from shutil import which

To keep things a little more concise, you can also import ``which`` directly
from ``shutilwhich``::

  from shutilwhich import which

This will still monkeypatch the ``shutil`` module. On Python 3.3 and above, the
module never do anything but return the stdlib ``shutil.which`` function.


