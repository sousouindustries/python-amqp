=============================
AMQP 1.0 library for Python 3
=============================


TODO
====
-   Implement the AMQP ``decimal`` types.
-   Input validation for ``Encodable``. At the current version,
    no validation is performed. This could cause e.g. an ``uint``,
    which is a scalar type, to hold a Python dictionary as its
    value.
