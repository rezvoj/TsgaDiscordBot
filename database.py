import contextlib, sqlite3



@contextlib.contextmanager
def transaction(connection: sqlite3.Connection, readOnly = False):
    cursor = connection.cursor()
    try:
        cursor.execute('BEGIN DEFERRED TRANSACTION' if readOnly else 'BEGIN')
        yield cursor
        if not readOnly:
            connection.commit()
    except Exception as ex:
        connection.rollback()
        raise ex
    finally:
        cursor.close()
        if readOnly:
            connection.rollback()


def getConnection(dbFile):
    return sqlite3.connect(dbFile, check_same_thread=False)
