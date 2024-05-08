#!/usr/bin/env python3
"""
reverseLog - Extract a reverse CABRILLO log file from QSOs already 
             in the QSO database.
"""
DEBUG = True

from reverselog.__init__ import VERSION
from moqputils.moqpdbutils import *
from moqputils.configs.moqpdbconfig import *
from datetime import datetime
from htmlutils.htmldoc import *
from cabrilloutils.CabrilloUtils import CabrilloUtils
from cabrillolog.logfile import logFile
from cabrillolog.qso import QSO

from qrzutils.qrz.qrzlookup import QRZLookup


class reverseLog(logFile): 
    def __init__(self, args = None):
        super().__init__() # Call parent to create logFile object
        self.args = args
        if args:
            self.appMain(args)
            
    def appMain(self, args):
        if args.callsign:
            db = MOQPDBUtils(HOSTNAME, USER, PW, DBNAME)
            db.setCursorDict()
            self.header.CALLSIGN = args.callsign.upper()
            logid = db.CallinLogDB(self.header.CALLSIGN)
            if logid:
                print('Call {} in database as log id {}.'.format(\
                        self.header.CALLSIGN, logid))
                return None
            self.header.CONTEST = 'MO-QSO-PARTY'
            self.header.CREATED_BY = 'N0SO Reverse Log Tool V{}'.format(VERSION)
            self.header.CATEGORY_OPERATOR = 'CHECKLOG'
            self.header.LOCATION = args.location.upper()
            self.getOpData(self.header.CALLSIGN)
            self.getQSOs(self.header.CALLSIGN, db)
            self.displayLog()
                
    def displayLog(self):
        for l in self.PrettyPrint():
            print(l)        
 
    def getQSOs(self, callsign, db):
        cu = CabrilloUtils()
        """
        Get qsos where urcall matches callsign
        """
        qsos = db.read_query("""SELECT * FROM QSOS 
                  WHERE URCALL = '{}' order by DATETIME""".format(callsign)) 
        for q in qsos:
            #print(q)
            nextQ=QSO()
            nextQ.parseQSO(q)
            """Copy MYxxx to URxxx and fill callsign/qth in MYxxx"""
            mycall = nextQ.urcall
            myqth = nextQ.urqth
            nextQ.urcall = nextQ.mycall
            nextQ.mycall = mycall
            nextQ.urqth = nextQ.myqth
            nextQ.myqth = myqth
            #nextQ.show()
            self.qsoList.append(nextQ)
            nextQ=None
        return self.qsoList   
        
    def getOpData(self, callsign):
        self.qrz=QRZLookup('/home/pi/Projects/moqputils/moqputils/configs/qrzsettings.cfg')
        if DEBUG: 
            print('Looking up {} ...'.format(callsign))

        try:
            opdata = self.qrz.callsign(callsign.strip())
            qrzdata=True
            #print(opdata
            if 'name_fmt' in opdata:
                self.header.NAME = opdata['name_fmt'].upper()
            elif ('fname' in opdata) and ('name' in opdata):
                self.header.NAME = ('{} {}'.format(\
                                                 opdata['fname'].upper(),
                                                 opdata['name'].upper()))
            elif ('attn' in opdata) and ('name' in opdata):
                self.header.NAME = ('{} ATTN {}'.format(\
                                                 opdata['name'].upper(),
                                                 opdata['att1'].upper()))
            elif ('name' in opdata):
                self.header.NAME = ('{}'.format(\
                                                 opdata['name'].upper()))
            else:
                self.header.NAME=('***NO NAME FOR {} ***'.format(\
                                                 op.upper()))
            if ('email' in opdata):
                self.header.EMAIL = opdata['email'].upper()                       
            else:                        
                self.header.EMAIL = '' 
            if ('addr1' in opdata):
                self.header.ADDRESS = opdata['addr1'].upper()
            else:
                self.header.ADDRESS = ''
            if ('addr2' in opdata):
                self.header.ADDRESS_CITY = opdata['addr2'].upper()
            else:
                self.header.ADDRESS_CITY = ''
            if ('state' in opdata):
                self.header.ADDRESS_STATE_PROVINCE = opdata['state'].upper()
            else:
                self.header.ADDRESS_STATE_PROVINCE = ''
            if ('zip' in opdata):
                self.header.ADDRESS_POSTALCODE = opdata['zip'].upper()
            else:
                self.header.ADDRESS_POSTALCODE = ''
            if ('country' in opdata):
                self.header.ADDRESS_COUNTRY = opdata['country'].upper()
            else:
                self.header.ADDRESS_COUNTRY = ''
        except:
            qrzdata=False
            self.header.NAME = ('NO QRZ for {}'.format(callsign))
            print('*** {} ***'.format(self.header.NAME))
        return qrzdata

class orphanCall():
    
    def __init__(self, callsign = None, 
                       workedby = [],
                       opname = None,
                       opemail = None,
                       db = None,
                       lookupcall = True):
        self.callsign = callsign
        self.workedBy = workedby
        self.opname = opname
        self.opemail = opemail
        if callsign and lookupcall:
            self.getOpData(callsign)
        if db:
            self.fillworkedBy(db)
            

    def fillworkedBy(self, db):
        if DEBUG:
                print('Filling in stations workedBy for log orphan {}...'.format(self.callsign))
        #print(self.workedBy)
        qsos = db.read_query("""SELECT UNIQUE URCALL,MYCALL FROM QSOS 
                         WHERE URCALL LIKE '{}' ORDER BY MYCALL""".format(self.callsign))
        #print(len(qsos))
        self.workedBy = []
        for q in qsos:
            #print(q['MYCALL'])
            self.workedBy.append(q['MYCALL'])
            
        #print(self.workedBy)
        return self.workedBy
        
    def getVals(self):
        return (self.callsign, self.opname, self.opemail, self.workedBy)
        
    def getCSV(self):
        return ('{}\t{}\t{}\t{}'.format(self.callsign,
                                       self.opname,
                                       self.opemail,
                                       self.workedBy))
                                       
    def getHTML(self):
      return('<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.\
              format(self.callsign,
                     self.opname,
                     self.opemail,
                     self.workedBy))

   
    def getDict(self):
        return {'callsign':self.callsign,
                    'opname':self.opname,
                    'opemail':self.opemail,
                    'workedBy':self.workedBy}
        
        
    def fetchReport(self):
        db = MOQPDBUtils(HOSTNAME, USER, PW, DBNAME)
        db.setCursorDict()
        tableData = db.read_query("""SELECT * FROM ORPHANS WHERE 1 ORDER BY UNIQUESTATIONS DESC;""")
        if (tableData == None) or (len(tableData) == 0):
            print("No data - run mqporphans --create first.")
            exit(0)
        self.reportData = self.makeReport(tableData)
        tstatus = db.read_query("""SHOW TABLE STATUS 
                  FROM {} LIKE 'LOGHEADER';""".format(DBNAME))
        self.Update_time = tstatus[0]['Update_time']          
        return tableData

    def makeReport(self, td):
        reportdata = [\
          'ORPHAN CALL\tUNIQUE STATION COUNT\tTOTAL QSOS\tWORKED BY']
        
        for uc in td:
            reportdata.append('{}\t{}\t{}\t{}'.format(\
                                                  uc['ORPHANCALL'],
                                                  uc['UNIQUESTATIONS'],
                                                  uc['TOTALQSOS'],
                                                  uc['WORKEDBY'])) 
                                                  
        self.reportData = reportdata
        return reportdata
        
    def showReport(self):
        for l in self.reportData:
            print(l)
            
    def appMain(self):
        self.showReport()
 
