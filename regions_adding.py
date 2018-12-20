#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Lenovo
#
# Created:     19.12.2018
# Copyright:   (c) Lenovo 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sqlite3
import sys, os
from codecs import open
def main():

    try:
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_NAME = 'sqlite.db'
        CONNECTION = sqlite3.connect(os.path.join(CURRENT_DIR, DATABASE_NAME))

        csv_file = open('regions.txt', 'r', 'utf-8')

        CONNECTION.cursor().execute('''
        DROP TABLE IF EXISTS regions;
        ''')
        CONNECTION.commit()


        CONNECTION.cursor().execute('''
        CREATE TABLE regions(
           city TEXT NOT NULL,
           county TEXT NOT NULL,
           code TEXT NOT NULL,
           region TEXT NOT NULL,
           capital TEXT NOT NULL
        );
        ''')
        CONNECTION.commit()

        for line in csv_file:

            fields = line.strip().split(';')
            print str(fields)
            cmd = u'''
                    INSERT INTO regions(city, county, code, region, capital) VALUES("%s");
                ''' % u'","'.join(fields)
            row = CONNECTION.cursor().execute(cmd)
        CONNECTION.commit()


        print 'Done'
    except:
        print str(sys.exc_info()[:2])
if __name__ == '__main__':
    main()
