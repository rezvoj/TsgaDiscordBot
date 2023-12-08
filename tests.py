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


    def testRemoveForUser(self):
        database.initDB(self.connection)
        userId1, userId2 = 12345, 67890
        streamerId1, streamerId2 = 111, 222
        status1, status2 = 1, 2
        with database.transaction(self.connection) as cursor:
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (streamerId1, 0))
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (streamerId2, 0))
            cursor.execute("INSERT INTO WatchedStatus (streamerId, userId, status) VALUES (?, ?, ?)", (streamerId1, userId1, status1))
            cursor.execute("INSERT INTO WatchedStatus (streamerId, userId, status) VALUES (?, ?, ?)", (streamerId1, userId1, status2))
            cursor.execute("INSERT INTO WatchedStatus (streamerId, userId, status) VALUES (?, ?, ?)", (streamerId2, userId1, status1))
            cursor.execute("INSERT INTO WatchedStatus (streamerId, userId, status) VALUES (?, ?, ?)", (streamerId2, userId2, status1))
        database.removeForUser(self.connection, userId1)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT * FROM WatchedStatus WHERE userId = ?", (userId1,))
            self.assertEqual(cursor.fetchall(), [])
            cursor.execute("SELECT * FROM Streamer WHERE id = ?", (streamerId1,))
            self.assertIsNone(cursor.fetchone())
            cursor.execute("SELECT * FROM Streamer WHERE id = ?", (streamerId2,))
            self.assertIsNotNone(cursor.fetchone())
        with database.transaction(self.connection) as cursor:
            cursor.execute("INSERT INTO WatchedStatus (streamerId, userId, status) VALUES (?, ?, ?)", (streamerId1, userId1, status1))
            cursor.execute("INSERT INTO WatchedStatus (streamerId, userId, status) VALUES (?, ?, ?)", (streamerId1, userId1, status2))
        database.removeForUser(self.connection, userId1, streamerId1, status1)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT * FROM WatchedStatus WHERE userId = ? AND streamerId = ? AND status = ?", (userId1, streamerId1, status1))
            self.assertEqual(cursor.fetchall(), [])
            cursor.execute("SELECT * FROM WatchedStatus WHERE userId = ? AND streamerId = ?", (userId1, streamerId1))
            self.assertNotEqual(cursor.fetchall(), [])
        database.removeForUser(self.connection, userId1, streamerId2)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT * FROM WatchedStatus WHERE userId = ? AND streamerId = ?", (userId1, streamerId2))
            self.assertEqual(cursor.fetchall(), [])
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT * FROM Streamer WHERE id = ?", (streamerId2,))
            self.assertIsNotNone(cursor.fetchone())


    def testGetStreamerStatus(self):
        database.initDB(self.connection)
        with database.transaction(self.connection) as cursor:
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (111, 5))
        status = database.getStreamerStatus(self.connection, 111)
        self.assertEqual(status, "5")
        status = database.getStreamerStatus(self.connection, 222)
        self.assertIsNone(status)


    def testGetStreamers(self):
        database.initDB(self.connection)
        with database.transaction(self.connection) as cursor:
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (111, 5))
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (222, 10))
        streamers = database.getStreamers(self.connection)
        expectedStreamers = [("111", "5"), ("222", "10")]
        self.assertEqual(streamers, expectedStreamers)


    def testUpdateStreamerStatus(self):
        database.initDB(self.connection)
        with database.transaction(self.connection) as cursor:
            cursor.execute("INSERT INTO Streamer (id, status) VALUES (?, ?)", (111, 5))
        database.updateStreamerStatus(self.connection, 111, 20)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT status FROM Streamer WHERE id = ?", (111,))
            status = cursor.fetchone()[0]
            self.assertEqual(status, 20)
        database.updateStreamerStatus(self.connection, 333, 15)
        with database.transaction(self.connection, readOnly=True) as cursor:
            cursor.execute("SELECT * FROM Streamer WHERE id = ?", (333,))
            result = cursor.fetchone()
            self.assertIsNone(result)



if __name__ == '__main__':
    unittest.main()
