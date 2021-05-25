#!/bin/python3

from functools import reduce

class OverwriteNotAllowed(Exception):
    """
    Custom overerite not allowed exception, with and option of 
    Providing a custom message when raising the exception
    """
    def __init__(self, message="Overwrite Not Allowed"):
        self.message = message
        super().__init__(self.message)

class Database:
    """
    """

    """
    __init__ will create attributes (tables) for Database classs based on 
    table names passed in at instantiation time.

    """
    def __init__(self, tables):
        if isinstance(tables, list):
            for table_name in tables:
                setattr(Database, table_name, self.Table(table_name))
        else:
            raise Exception("Database tables must be passed as list")
    
    """
    Table class to implement oprartions to table object
    Will contain the database attribute where the data to this table is
    stored

    """

    class Table:
        """
        Will keep our data in this object called database
        """
        database = {}
        """
        This will keep temporary transaction  information required for rollback
        """
        _transaction_queue = [] #  temp values to update (insert, delete, delete)
        _transaction_copy  = {}  # copy of database values before this update

        """
        Flag to enable disable transactions
        """
        auto_commit = True


        def __init__(self, name):
            self.table_name = name

        """
        Will use this to keep a copy of ouf our database values before we
        modify them so that we can use them to rollback
        _del flag will indicate a del transaction
        """
        def prepare_transaction(self, key, value, _del=False):
            #will only keep key for delete values
            data = {key:value} if not _del else {"key":key}
            self._transaction_queue.append(
                {
                    'update': not _del, 
                    'data':data
                }
            )
            if key in self.database:
                self._transaction_copy.update({key:self.database.get(key)})

        """
        Clear transaction once done
        """
        def clear_transaction(self):
            self._transaction_queue.clear()
            self._transaction_copy.clear()

        def insert(self, values):
            if isinstance(values, dict):
                for key, value in values.items():
                    
                    if key in self.database:
                        # will also rollback if we are in transaction mode
                        if not self.auto_commit:
                            self.rollback()
                        raise OverwriteNotAllowed(
                                "You are not allowed to overwrite values "
                                "already existing in database"
                        )
                    if not self.auto_commit:
                        self.prepare_transaction(key, value)
                    else:
                        self.database.update({key:value})

            else:
                raise Exception("Invalid values supplied for %s insert"\
                    % self.table_name)

        def delete(self, keys_list):
            for key in keys_list:
                if key in self.database:
                    if not self.auto_commit:
                        #pass in _del=True
                        self.prepare_transaction(key, None, True)
                    else:
                        self.database.pop(key)
                else:
                    if not self.auto_commit:
                        self.rollback()
                        raise Exception("Delete key [%s] not found" % key)


        def transaction(self):
            self.auto_commit = False

        def no_transaction(self):
            self.auto_commit = True

        """
        Commit new changes atomically in FIFO (First in First Out)
        When done with commit rest auto_commit to True
        """
        def commit(self):
            try:
                for transaction in self._transaction_queue:
                    if transaction.get('update') == True:
                        self.database.update(transaction.get('data'))
                    else:
                        self.database.pop(transaction.get('data').get('key'))

                self.clear_transaction()
            except(Exception) as ex:
                self.rollback()
                raise Exception(ex)
            finally:
                self.auto_commit=True

        # dicard any new changes
        def rollback(self):
            self.database.update(self._transaction_copy)
            self.clear_transaction()
            self.auto_commit=True

        def mean(self):
            if self.database:
                return reduce(
                        lambda a, b: a + b, self.database.values()
                        ) / len(self.database)
            return 0

        """
        In order to get items from db using indexed notation e.g
        database[0] we define __getitem__
        """
        def __getitem__(self, index):
            if index in self.database:
                return self.database.get(index)
            raise Exception("Item Not Found")
    
if __name__ == '__main__':
    db = Database(tables=["temperature", "pressure"])

    # Insert three items immediately
    db.temperature.insert({10: 10, 20: 11, 30: 9})
    print('Mean temperature=', db.temperature.mean(), '- expected value=10')
    print('Temperature at "20"=', db.temperature[20], '- expected value=11')

    # Begin a new transaction
    db.temperature.transaction()

    # Insert two items - queued
    db.temperature.insert({40: 19, 50: 21})
    # Delete one - queued
    db.temperature.delete([10])
    print('Mean temperature=', db.temperature.mean(), '- expected value=10')

    # Discard all operations in the current transaction
    db.temperature.rollback()
    print('Mean temperature=', db.temperature.mean(), '- expected value=10')

    # Start a new one
    db.temperature.transaction()

    # Do some operations...
    db.temperature.insert({40: 0, 50: 2})
    db.temperature.delete([20, 30])
    print('Mean temperature=', db.temperature.mean(), '- expected value=10')

    # Write them to the database
    db.temperature.commit()
    print('Mean temperature=', db.temperature.mean(), '- expected value=4')

    # Attempt to insert a new value with already existing index value - will raise an error
    db.temperature.insert({10: 20})
