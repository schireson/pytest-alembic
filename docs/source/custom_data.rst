Custom data
===========

To preempt the need to write an explicit test for every new migration,
there is a mechanism built into the config to automatically insert data
into the database before or upon reaching a given revision.

To that end:

.. code-block:: python

   @pytest.fixture
   def alembic_config():
       return {
           "before_revision_data": {
               "fb4d3ab5f38d": [
                   {"__tablename__": "foo", "id": 1, "name": "foo"},
                   {"__tablename__": "bar", "id": 1, "name": "bar"},
               ],
           },
           "at_revision_data": {
               "a5a9ccc4e535": {
                   "__tablename__": "foo",
                   "id": 1,
                   "name": "foo2",
               },
           },
       }


There are two, similiar but distinct options. :code:`before_revision_data`, and :code:`at_revision_data`.

* :code:`before_revision_data` will insert the given data for all upgrade commands before performing
  the upgrade to the given revision.
* :code:`at_revision_data` will insert the given data for all upgrade commands after having performed
  the upgrade to the given revision.

To be clear, you can use either of them to describe the same operation. But depending on the
circumstance (if for example, you are testing a real-world situation that you are trying to
semantically model more closely), one or the other option may be more appropriate.

.. warning::

   Both :code:`before_revision_data` and :code:`at_revision_data` internally issue ``commit``
   during the migration process (a side-effect of how Alembic works, and how it integrates
   with this library).

   If you rely upon the database state to be able to be rolled back after the migrations have run,
   you may not be able to use this feature.

Schema
------

The value for either :code:`before_revision_data` or :code:`at_revision_data`, should be a :func:`dict`
where the keys are the revision for which the data is being described.

The value can either be a :func:`dict` (single row), or a :func:`list` of :func:`dict` (multiple
rows). :code:`__tablename__` is a special key which tells us the name of the table to insert the
data into, and the rest of the spec should describe the columns and the column data for that row,
similar to what you might do for a :meth:`table.insert().values(...) <sqlalchemy.sql.expression.Insert.values>` call.

Alternatively, you can directly import and instantiate a :class:`RevisionSpec` and set that as the
value to  either :code:`before_revision_data` or :code:`at_revision_data`.

Example
-------
Given the above data, and history of:

.. code-block:: text

   23256c7bf855 > fb4d3ab5f38d -> a5a9ccc4e535 -> b835ae9ff1d1

We would:

* Upgrade to 23256c7bf855
* Insert
  :code:`{"__tablename__": "foo", "id": 1, "name": "foo"}` and
  :code:`{"__tablename__": "bar", "id": 1, "name": "bar"}`

* Upgrade to fb4d3ab5f38d
* Upgrade to a5a9ccc4e535
* Insert
  :code:`{"__tablename__": "foo", "id": 1, "name": "foo2"}`
* Upgrade to b835ae9ff1d1
