class OverwriteNotAllowed(Exception):
    """
    """

class Database:
    """
    """

    class Table:
        """
        Will keep our data in this object
        """
        data = {}

        def __init__(self, name):
            self.table_name = name

        def insert(self, values):
            if isinstance(values, dict):
                for key, value in values:
                    if self.data.contains_key(key):
                        raise OverwriteNotAllowed("Override not allowed")
                    self.data.update({key:value})
            else:
                raise Exception("Invalid values supplied for %s insert"\
                    %s self.table_name)

        def delete(self, value):
            print("called delete")

        def transaction(self):
            print("called transaction")

        def rollback(self):
            print("called rollback")
    
    def __init__(self, tables):
        if isinstance(tables, list):
            for table_name in tables:
                setattr(Database, table_name, self.Table(table_name))
        else:
            raise Exception("Database tables must be passed as list")
        
    def _print(self):
        print([n for n in self.__class__.__dict__ if not n.startswith('__')])
         
        
if __name__ == '__main__':
    db=Database(tables=['temperature', 'pressure'])
    print db.temperature
    db.temperature.insert({"10:10"})
    print db.pressure
    db.pressure.insert({"10":"10"})
    
#if __name__ == '__main__':
#    db = Database(tables=['temperature', 'pressure'])
#
#    # Insert three items immediately
#    db.temperature.insert({10: 10, 20: 11, 30: 9})
#    print('Mean temperature=', db.temperature.mean(), '- expected value=10')
#    print('Temperature at "20"=', db.temperature[20], '- expected value=11')
#
#    # Begin a new transaction
#    db.temperature.transaction()
#
#    # Insert two items - queued
#    db.temperature.insert({40: 19, 50: 21})
#
#    # Delete one - queued
#    db.temperature.delete([10])
#    print('Mean temperature=', db.temperature.mean(), '- expected value=10')
#
#    # Discard all operations in the current transaction
#    db.temperature.rollback()
#    print('Mean temperature=', db.temperature.mean(), '- expected value=10')
#
#    # Start a new one
#    db.temperature.transaction()
#
#    # Do some operations...
#    db.temperature.insert({40: 0, 50: 2})
#    db.temperature.delete([20, 30])
#    print('Mean temperature=', db.temperature.mean(), '- expected value=10')
#
#    # Write them to the database
#    db.temperature.commit()
#    print('Mean temperature=', db.temperature.mean(), '- expected value=4')
#
#    # Attempt to insert a new value with already existing index value - will raise an error
#    db.temperature.insert({10: 20})
