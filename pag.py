import csv
import argparse

def parse_elsi_student_teacher_ratios(in_dir):

    def pgen(file_name, writer, fips_prefix, region_type, type_prefix, id_prefix):
        input_file = csv.DictReader(open(file_name))

        for row in input_file:
            id=None
            name=None
            variable='student-teacher-ratio'
            type=region_type.lower()
            year_value=[]
            value=[]

            for k in row.keys():
                #print k
                if(k.startswith(fips_prefix)): #e.g. ANSI
                    #print row[k]
                    if(row[k]!=None):
                        try:
                            int(row[k])
                            id=id_prefix+row[k]
                        except:
                            print "including " + str(name) + " but FIPS code: " + str(row[k]) + " not resolvable. Add to autosuggest exclusion dataset"

                elif(k.startswith("Pupil")):
                    year = str(int((k.split(type_prefix)[1][:4]))+1)
                    try: #check for legit float values
                        float(row[k])
                        value=row[k]
                    except ValueError:
                        value=None

                    year_value.append((year, value))
                elif(k.endswith(" Name")): #weird chars in the export
                    name=row[k]
            if (id!=None):
                for yv in sorted(year_value, key=lambda tup: tup[0]):
                    writer.writerow({'id': id, 'name': name, 'type': type, 'variable': variable, 'year': yv[0], 'value':yv[1]})

    print "parsing " + in_dir + "/teacher-student-ratios-states.csv"

    with open('teacher-student-ratios-merged.csv', 'w') as csvfile:
        fieldnames=['id', 'name', 'type', 'variable', 'year', 'value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        pgen(in_dir + "/teacher-student-ratios-counties.csv", writer, "County Number", "County", "Pupil/Teacher Ratio [Public School] ", "0500000US")
        pgen(in_dir + "/teacher-student-ratios-states.csv", writer, "ANSI", "State", "Pupil/Teacher Ratio [State] ", "0400000US")

    print "done"

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
        parse_elsi_student_teacher_ratios("data/"+args.p)

        """
        Add other data sources here. Stick to the source/variable naming convention.
        """
    else:
        print "unknown cat/subcat data source specified"

