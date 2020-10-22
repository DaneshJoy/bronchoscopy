import sqlite3
from sqlite3 import Error
import os


class PatientsDB():
    def db_createConnection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='patients' ''')

            if not cursor.fetchone()[0]==1:
                cursor.execute('''CREATE TABLE IF NOT EXISTS patients(
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                date DATE,
                                image TEXT,
                                segmented BOOLEAN NOT NULL CHECK(segmented IN (0,1)),
                                centerline BOOLEAN NOT NULL CHECK(centerline IN (0,1)),
                                registered BOOLEAN NOT NULL CHECK(registered IN (0,1))
                                );''')
                conn.commit()
        except Error as e:
            print('Error while connecting to the database\n', e)
            # self.conn.close()
            # print('Database connection is closed')

        return conn
    
    def db_addPatient(self, conn, patient):
        """
        Create a new patient into the patients table
        :param conn:
        :param patient:
        :return: patient id
        """
        sql = ''' INSERT INTO patients(name, date, image, segmented, centerline, registered)
                VALUES (?, ?, ?, ?, ?, ?); '''
        cur = conn.cursor()
        cur.execute(sql, patient)
        conn.commit()
        return cur.lastrowid

    def db_updatePatient(self, conn, patient):
        """
        update segmented, centerline, and registered flags of a patient
        :param conn:
        :param patient:
        """
        sql = ''' UPDATE patients
                SET segmented=? ,
                    centerline=? ,
                    registered=?
                WHERE name=? '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()

    def db_getPatients(self, conn):
        """
        Query all rows in the patients table
        :param conn: the Connection object
        :return: patients
        """
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients")

        rows = cur.fetchall()
        return rows

    def db_getPatient(self, conn, name):
        """
        Query patients by name
        :param conn: the Connection object
        :param name:
        :return: seleted patient
        """
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE name=?", (name,))

        rows = cur.fetchall()
        return rows

    def db_deletePatient(self, conn, name):
        """
        Delete a patient by name
        :param conn:  Connection to the SQLite database
        :param name: name of the patient
        :return:
        """
        sql = 'DELETE FROM patients WHERE name=?'
        cur = conn.cursor()
        cur.execute(sql, (name,))
        conn.commit()
    
    def db_deleteAllPatients(self, conn):
        """
        Delete all patients in the DB
        :param conn: Connection to the SQLite database
        :return:
        """
        sql = 'DELETE FROM patients'
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()