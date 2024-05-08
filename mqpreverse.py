#!/usr/bin/env python3
import os.path
import sys

whereami = os.path.split( os.path.realpath(__file__) )
pathsplit = os.path.split(whereami[0])
#print("here I am :", whereami, pathsplit)

DEVMODPATH = [pathsplit[0],
              '/home/pi/Projects', 
              '/home/pi/Projects/moqputils',
              '/home/pi/Projects/cabrillolog']
#print('Using DEVMODPATH=',DEVMODPATH)
#os.chdir(pathsplit[0])

for mypath in DEVMODPATH:
        if ( os.path.exists(mypath) and \
          (os.path.isfile(mypath) == False) ):
            sys.path.insert(0, mypath)

import argparse
from reverselog.__init__ import VERSION

USAGE = \
"""
mqpreverse
"""

DESCRIPTION = \
"""
Extract a reverse CABRILLO log file from QSOs already in the QSO 
database.

"""

EPILOG = \
"""
That is all!
"""

def parseMyArgs():
    parser = argparse.ArgumentParser(\
                    description = DESCRIPTION, usage = USAGE)
    parser.add_argument('-v', '--version', 
                        action='version', 
                        version = VERSION)
    
    parser.add_argument('-c', '--callsign',
                                   default=None,
            help="""Callsign to create the reverse log for.""")

    parser.add_argument('-l', '--location',
                                   default='MO',
            help="""value to use in the CABRILLO header LOCATION: field.
                    Default = MO (this is the MOQP after all!).""")

    parser.add_argument('-q', '--qth',
                                   default = 'SLC',
            help="""Value to fill the MYQTH part of each QSO: field
                    with. Default = SLC ( St. Louis County -- this is 
                    the MOQP after all!).""")

    parser.add_argument('-t', '--reportType',
                                   choices = ['cab', 'csv', 'html'],
                                   default = 'cab',
            help="""Set report type for output. Only valid if more than
                    one report output type is avaible. Options are: 
                    cab (CABRILLO), csv (Comma Separated Variables) or 
                    html for web page use. Default value is cab""")


    args = parser.parse_args()
    return args
    
    
if __name__ == '__main__':
    args = parseMyArgs()
    if args.callsign:
        from reverselog.reverseLog import reverseLog
        app = reverseLog(args)

