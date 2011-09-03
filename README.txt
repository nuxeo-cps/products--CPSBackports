===================
CPSBackports README
===================

:Author: Georges Racinet <gracinet@cps-cms.org>


Contents
========

- `Features`_
- `Install`_


Features
========
This product backports some transversal features from CPS > 3.5 to
older versions, for administration uniformity.
If possible, they are to be used in the same way as in modern versions.

CPS Jobs
--------
High level helper to run command-line scripts called jobs against a CPS
installation (a much better alternative to external methods). This
approach is the recommended one in the CPS 3.5 series.

Some standard jobs are provided in the ``jobs/`` subdirectory.
Check ``doc/jobs.txt`` for more details.


Install
=======

Enabling backports
------------------
Putting this Products in one of your Products directory enables all
backports.

In the future, it should be possible to disable some of them by a simple
configuration file.

Requirements
------------

There is no minimum version requirement.
Some backports may check the CPS version or the Zope version to
withdraw themselves.

Optionnally, one may disable some backports by listing them in a file
named ```backports.conf```.



.. Emacs
.. Local Variables:
.. mode: rst
.. End:
.. Vim
.. vim: set filetype=rst:
