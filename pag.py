import argparse
import urllib
import json
import traceback
import os
import sys
sys.path.append( "src" )

import elsi
import bea

parser = argparse.ArgumentParser()
parser.add_argument('-a', help="shows available raw datasets for transformation", action='store_true')
parser.add_argument('-p', help="parses specified data dir and generates latest transform, e.g. elsi/student-teacher-ratios", default=None)
args = parser.parse_args()

if(args.a):
    import os
    for cat in next(os.walk("data"))[1]:
        scats = next(os.walk("data/"+cat))[1]
        for scat in scats:
            print cat+"/"+scat

elif(args.p):
    if(args.p=="elsi/student-teacher-ratios"):
        elsi.parse_elsi_student_teacher_ratios("data/"+args.p)
    elif(args.p=="elsi/expenditures"):
        elsi.parse_elsi_expenditures("data/"+args.p)
    elif(args.p=="elsi/enrollments"):
        elsi.parse_elsi_enrollments("data/"+args.p)
    elif(args.p=="elsi/schools"):
        elsi.parse_elsi_schools("data/"+args.p, "public-schools-usa.csv", "schools")
    elif (args.p == "bea/personal_income"):
        bea.parse_bea_personal_income("data/" + args.p)

        """
        Add other data sources here. Stick to the source/variable naming convention.
        """
    else:
        print "unknown cat/subcat data source specified"

