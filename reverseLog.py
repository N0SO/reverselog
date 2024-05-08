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

