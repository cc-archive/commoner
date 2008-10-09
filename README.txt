========
COMMONER
========

:Author: Nathan R. Yergler <nathan@creativecommons.org>
:Organization: `Creative Commons <http://creativecommons.org>`_
:Copyright: 
   2008, Nathan R. Yergler, Creative Commons; 
   licensed to the public under the `AGPL v3 or later 
   <http://www.fsf.org/licensing/licenses/agpl.html>`_.
   See LICENSE for details.

Commoner is an application which implements a basic work registry and
supports ccREL/RDFa based discovery of work information.

Installation
============

Commoner uses `buildout <http://python.org/pypi/zc.buildout>`_ to
manage dependencies.  Buildout will handle retrieving most
dependencies for you.  To get started, run::

  $ python bootstrap.py

This will download `setuptools <>`_ and create the buildout script.
To retrieve dependencies and create control scripts run::

  $ ./bin/buildout

Before you can run Commoner you need to decide on a database to use.
Commoner can run on any database supported by Django, including
sqlite, MySQL, and PostgreSQL.  If you are using something other than
sqlite, you'll need to create your database before continuing.

MySQL Notes
-----------

The default character set for MySQL is latin1. When creating your
database you will need to specify the character set as utf8::

  mysql> create database commoner charset=utf8;


Development
===========

Running Tests
=============
