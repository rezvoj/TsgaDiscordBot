import unittest, database, os 



class DatabaseTests(unittest.TestCase):

    def setUp(self):
        self.dbFile = 'testDatabase.db'
        self.connection = database.getConnection(self.dbFile)


    def tearDown(self):
        self.connection.close()
        if os.path.exists(self.dbFile):
            os.remove(self.dbFile)


    def testInitDB(self):
        database.initDB(self.connection)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("PRAGMA table_info(Streamer)")
            streamerColumns = cursor.fetchall()
            expectedStreamerColumns = [
                (0, 'id', 'BIGINT', 1, None, 1),
                (1, 'status', 'BIGINT', 1, None, 0)
            ]
            self.assertEqual(streamerColumns, expectedStreamerColumns)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("PRAGMA table_info(WatchedStatus)")
            watchedStatusColumns = cursor.fetchall()
            expectedWatchedStatusColumns = [
                (0, 'streamerId', 'BIGINT', 1, None, 1),
                (1, 'userId', 'BIGINT', 1, None, 2),
                (2, 'status', 'BIGINT', 1, None, 3)
            ]
            self.assertEqual(watchedStatusColumns, expectedWatchedStatusColumns)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("PRAGMA foreign_key_list(WatchedStatus)")
            foreignKeys = cursor.fetchall()
            expectedForeignKeys = [
                (0, 0, 'Streamer', 'streamerId', 'id', 'NO ACTION', 'NO ACTION', 'NONE')
            ]
            self.assertEqual(foreignKeys, expectedForeignKeys)


    def testAddStreamerUserStatus(self):
        database.initDB(self.connection)
        userId, streamerId, status = 12345, 67890, 1
        database.addStreamerUserStatus(self.connection, userId, streamerId, status)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT * FROM Streamer WHERE id = ?", (streamerId,))
            streamer = cursor.fetchone()
            expectedStreamer = (streamerId, -1)
            self.assertEqual(streamer, expectedStreamer)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute(
                "SELECT * FROM WatchedStatus WHERE streamerId = ? AND userId = ? AND status = ?",
                (streamerId, userId, status)
            )
            watchedStatus = cursor.fetchone()
            expectedWatchedStatus = (streamerId, userId, status)
            self.assertEqual(watchedStatus, expectedWatchedStatus)
        database.addStreamerUserStatus(self.connection, userId, streamerId, status)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM WatchedStatus WHERE streamerId = ? AND userId = ? AND status = ?",
                (streamerId, userId, status)
            )
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)
        existingStreamerId, existingStatus = 54321, 0
        with database.transaction(self.connection) as cursor:
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (existingStreamerId, existingStatus))
        database.addStreamerUserStatus(self.connection, userId, existingStreamerId, status)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT * FROM Streamer WHERE id = ?", (existingStreamerId,))
            existingStreamer = cursor.fetchone()
            expectedExistingStreamer = (existingStreamerId, existingStatus)
            self.assertEqual(existingStreamer, expectedExistingStreamer)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute(
                "SELECT * FROM WatchedStatus WHERE streamerId = ? AND userId = ? AND status = ?",
                (existingStreamerId, userId, status)
            )
            watchedStatusExisting = cursor.fetchone()
            expectedWatchedStatusExisting = (existingStreamerId, userId, status)
            self.assertEqual(watchedStatusExisting, expectedWatchedStatusExisting)



if __name__ == '__main__':
    unittest.main()
