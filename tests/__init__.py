"""Shared helpers for the test suite.

The sqlalchemy version guards that used to live here -- ``requires_asyncio_support``
and ``requires_sqlalchemy_2`` -- are gone. Both asked whether the installed sqlalchemy
was new enough to have ``ext.asyncio``, and the declared floor is now 2.0, so the
answer is always yes and the skips could never fire. ``requires_sqlalchemy_2`` was
already unreferenced.
"""
