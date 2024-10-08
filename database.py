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


def initDB(connection: sqlite3.Connection):
    with transaction(connection) as cursor:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Streamer (
            id BIGINT PRIMARY KEY NOT NULL,
            status BIGINT NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS WatchedStatus (
            streamerId BIGINT NOT NULL,
            userId BIGINT NOT NULL,
            status BIGINT NOT NULL,
            PRIMARY KEY (streamerId, userId, status),
            FOREIGN KEY (streamerId) REFERENCES Streamer(id)
        )
        ''')


def addStreamerUserStatus(connection: sqlite3.Connection, userId, streamerId, status):
    with transaction(connection) as cursor:
        userId, streamerId, status = int(userId), int(streamerId), int(status)
        cursor.execute("SELECT * FROM Streamer WHERE id = ?", (streamerId,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (streamerId, -1))
        cursor.execute(
            '''
            INSERT INTO WatchedStatus (streamerId, userId, status)
            VALUES (?, ?, ?)
            ON CONFLICT(streamerId, userId, status) 
            DO NOTHING
            ''', (streamerId, userId, status)
        )


def removeForUser(connection: sqlite3.Connection, userId, streamerId = None, status = None):
    with transaction(connection) as cursor:
        userId = int(userId)
        if streamerId is None:
            cursor.execute("DELETE FROM WatchedStatus WHERE userId = ?", (userId,))
            cursor.execute("DELETE FROM Streamer WHERE NOT EXISTS (SELECT 1 FROM WatchedStatus WHERE Streamer.id = WatchedStatus.streamerId)")
        else:
            streamerId = int(streamerId)
            if status is None:
                cursor.execute("DELETE FROM WatchedStatus WHERE userId = ? AND streamerId = ?", (userId, streamerId))
            else:
                cursor.execute("DELETE FROM WatchedStatus WHERE userId = ? AND streamerId = ? AND status = ?", (userId, streamerId, int(status)))
            cursor.execute("DELETE FROM Streamer WHERE id = ? AND NOT EXISTS (SELECT 1 FROM WatchedStatus WHERE Streamer.id = WatchedStatus.streamerId)", (streamerId,))


def getStreamerStatus(connection: sqlite3.Connection, streamerId):
    with transaction(connection, readOnly=True) as cursor:
        cursor.execute("SELECT status FROM Streamer WHERE id = ?", (int(streamerId),))
        status = cursor.fetchone()
        if status is not None:
            return str(status[0])
        return None


def getStreamers(connection: sqlite3.Connection):
    with transaction(connection, readOnly=True) as cursor:
        cursor.execute("SELECT * FROM Streamer")
        streamers = cursor.fetchall()
        return [(str(streamer[0]), str(streamer[1])) for streamer in streamers]


def updateStreamerStatus(connection: sqlite3.Connection, streamerId, status):
    with transaction(connection) as cursor:
        cursor.execute("UPDATE Streamer SET status = ? WHERE id = ?", (int(status), int(streamerId)))


def listForUser(connection: sqlite3.Connection, userId, streamerId = None):
    userId = int(userId)
    with transaction(connection, readOnly=True) as cursor:
        if streamerId is None:
            cursor.execute("SELECT streamerId, status FROM WatchedStatus WHERE userId = ?", (userId, ))
        else:
            cursor.execute("SELECT streamerId, status FROM WatchedStatus WHERE userId = ? AND streamerId = ?", (userId, int(streamerId)))
        resultList = dict()
        for watchedStatus in cursor.fetchall():
            streamer, status = str(watchedStatus[0]), str(watchedStatus[1])
            if streamer not in resultList:
                resultList[streamer] = list()
            resultList[streamer].append(status)
        return resultList


def getUsersForStreamerStatus(connection: sqlite3.Connection, streamerId, status):
    with transaction(connection, readOnly=True) as cursor:
        streamerId, status = int(streamerId), int(status)
        cursor.execute("SELECT userId FROM WatchedStatus WHERE streamerId = ? AND status = ?", (streamerId, status))
        return [str(watchedStatus[0]) for watchedStatus in cursor.fetchall()]
