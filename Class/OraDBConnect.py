import cx_Oracle  #there is also  pyodbc
from pprint import pprint
import logging
logger = logging.getLogger("AutoToolBox")

class OracleDBConnector:
 def __init__(self,dbHost,dbUser,dbPass,dbInstance,dbPort):
    # Build a DSN (can be subsitited for a TNS name)
    self.db=None
    self.dsn = cx_Oracle.makedsn(dbHost, dbPort, dbInstance)
    self.db = cx_Oracle.connect(dbUser, dbPass, self.dsn)
    print "DB Version" + self.db.version


 def query(self,querySQL):
    cursor = self.db.cursor()
    cursor.execute(querySQL)                #cursor.fetchone()
    #print cursor.description
    return cursor.fetchall()

 def __del__(self):
     if self.db:
      logger.debug("DB connection   is closing!")
      self.db.cursor().close()
      logger.debug("cursor is closed by DB Desctractor!")
      self.db.close()
      logger.debug("DB is closed by Desctractor!")




if __name__ == "__main__":
    db=OraDBConnect()
    result = db.query('select MANF_NAME from voucher_manufacturer');
    print result[1][0],type(result[1][0])
    #db.close()  #not needed with __del__



