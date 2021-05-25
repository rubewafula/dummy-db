# Problem

Task: Implement a "library" (a set of classes) working with a simple
transaction-supporting measurement database. The class Database expects a list
of variable names (tables) and allows the access to the tables as object
attributes, e.g. db.temperature. A table allows adding new values by calling
the insert method expecting a key:value data format (e.g. dictionary).
Duplicate values are not allowed, any attempt to overwrite a value for an
already existing key raises an error (overwriteNotAllowed). The delete method
allows removing existing measurements according to an argument specifying a
list of keys. The mean method returns an average value for a variable.
Individual measurements can be accessed by their key in the same way as for any
array access, i.e, by using the [] operator.

A table supports transactions for inserting and deleting data. Transactions are
atomic sets of multiple operations: the transaction method starts a new
new transaction. Inserting or deleting data within a transaction suspends the
actual execution of the operations until the commit method is called, i.e. the
operations in the transaction are queued and after a commit gets executed in
the FIFO (first in first out) order. A transaction can be discarded by calling
the rollback method. Both commit and rollback end the current transaction, a
new transaction has to be started explicitly. Operations called outside of a
transaction are executed immediately.

Submit a solution as one script named dummy-db.py using the file the template
file as a template. Use the existing code as an API description, i.e. your code
must work with the existing code in the template.

# dummy-db Dummy db class
implementation
