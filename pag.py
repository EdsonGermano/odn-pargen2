import csv
import argparse
import urllib
import json
import traceback

class ACSResolver(object):

    @staticmethod
    def _is_acs_type(region_type, acs_id):
        if (region_type=='msa'):
            if "310M200" in acs_id: return True
        elif (region_type=='state'):
            if "0400000" in acs_id: return True
        elif ("region_type")=='place':
            if "1600000" in acs_id: return True
        elif ("region_type")=="county":
            if "0500000" in acs_id: return True
        elif ("region_type")=="zip_code":
            if "8600000" in acs_id: return True
        else:
            return False

    @staticmethod
    def resolve(name, region_type="msa"):
        """
        Resolves ACS id and autosuggest name by fuzzy tokenized lookup
        @return id,autosuggest_name
        """

        if(region_type == "msa"):
            print "\nattempting fuzzy resolution of ACS code for " + str(name)
            metro = urllib.urlopen("https://odn.data.socrata.com/resource/7g2b-8brv.json?$select=id,autocomplete_name&$q="+name+"&$order=population%20desc&$limit=1").readline()
            json_match_results = json.loads(metro)
            id=json_match_results[0]["id"]
            name=json_match_results[0]["autocomplete_name"]
            if ACSResolver._is_acs_type(region_type, id):
                print "resolved id="+str(id)+", name="+str(name)
                return id,name

            msg = "Invalid id="+str(id)+" resolved for "+str(name)
            print msg
            raise Exception(msg)

class Enrollments(object):

    def __init__(self):
        self.id_year_value_map = dict()

        for row in csv.DictReader(open('enrollments-merged.csv')):
            if row["id"] not in self.id_year_value_map:
                self.id_year_value_map[row["id"]]=dict()

            self.id_year_value_map[row["id"]][row["year"]]=int(row["value"])

class ParseRule(object):

    def __init__(self, file_name, fips_prefix, region_type, type_prefix, id_prefix, fuzzy_resolve=False, normalize_per_student=False):
        self.file_name=file_name
        self.fips_prefix=fips_prefix
        self.region_type=region_type
        self.type_prefix=type_prefix
        self.id_prefix=id_prefix
        self.fuzzy_resolve=fuzzy_resolve
        self.normalize_per_student=normalize_per_student

class ELSITransformer(object):

    fieldnames=['id', 'name', 'type', 'variable', 'year', 'value']

    def __init__(self, subcategory, variable, data_path):
        self.subcategory=subcategory
        self.variable = variable
        self.data_path = data_path
        self.parse_rules=[]

    def transform(self):
        with open(self.subcategory+'-merged.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for r in self.parse_rules:
                self._transform_region(r, writer)

        print "done"

    def _transform_region(self, parse_rule, writer):
        enrollments=Enrollments()
        file_path=self.data_path + "/"+parse_rule.file_name
        print "parsing " + file_path

        input_file = csv.DictReader(open(file_path))

        i=0
        for row in input_file:
            i+=1

            id=None
            name=None
            type=parse_rule.region_type.lower()
            if type=="cbsa":type="msa"
            year_value=[]
            value=[]

            for k in row.keys():
                if(k.startswith(parse_rule.fips_prefix)): #e.g. ANSI
                    if(row[k]!=None):
                        try:
                            if(not parse_rule.fuzzy_resolve):
                                id = row[k]
                                # strip ="*" format if present
                                if id.startswith('=') and id.endswith('"'): id = id[2:-1]

                                int(id)
                                id=parse_rule.id_prefix+id
                        except:
                            print "including " + str(name) + " but FIPS code: " + str(row[k]) + " not resolvable. Add to autosuggest exclusion dataset"

                elif(k.startswith(parse_rule.type_prefix)):
                    year = str(int((k.split(parse_rule.type_prefix)[1].strip()[:4]))+1)
                    try: #check for legit float values
                        float(row[k])
                        value=row[k]
                    except ValueError:
                        value=None

                    year_value.append((year, value))
                elif(k.endswith(" Name")): #weird chars in the export
                    name=row[k]

            if(parse_rule.fuzzy_resolve):
                try:
                    id,name = ACSResolver.resolve(name, region_type=type)
                except:
                    print "failed to resolve name=" + str(name) + ", skipping"
                    continue

            if (id!=None):
                for yv in sorted(year_value, key=lambda tup: tup[0]):
                    writer.writerow({'id': id, 'name': name, 'type': type, 'variable': self.variable, 'year': yv[0], 'value':yv[1]})
                    if(parse_rule.normalize_per_student):
                        print yv[0]
                        print yv[1]
                        print enrollments.id_year_value_map[id][yv[0]]
                        normalized_value=int(float(yv[1])/enrollments.id_year_value_map[id][yv[0]])
                        print str(normalized_value)
                        print "\n"
                        writer.writerow({'id': id, 'name': name, 'type': type, 'variable': self.variable+"-per-student", 'year': yv[0], 'value':normalized_value})


            print "completed row %d\n" % i

def parse_elsi_student_teacher_ratios(in_dir):
    transformer = ELSITransformer("classroom_statistics", "student-teacher-ratio", in_dir)
    transformer.parse_rules.append(ParseRule("student-teacher-ratios-counties.csv", "County Number", "County", "Pupil/Teacher Ratio [Public School] ", "0500000US"))
    transformer.parse_rules.append(ParseRule("student-teacher-ratios-states.csv", "ANSI", "State", "Pupil/Teacher Ratio [State] ", "0400000US"))
    transformer.parse_rules.append(ParseRule("student-teacher-ratios-metros.csv", "ANSI", "CBSA", "Pupil/Teacher Ratio [Public School] ", "310M200US", fuzzy_resolve=True))
    transformer.transform()

def parse_elsi_expenditures(in_dir):
    transformer = ELSITransformer("expenditures", "administration-salaries", in_dir)
    print "shit"
    transformer.parse_rules.append(ParseRule("administration-salaries-expenditures-states.csv", "ANSI", "State", "School Administration - Salaries (E215) [State Finance]", "0400000US", normalize_per_student=True))
    print "shit"
    transformer.transform()

def parse_elsi_enrollments(in_dir):
    transformer = ELSITransformer("enrollments", "total-student-enrollments", in_dir)
    transformer.parse_rules.append(ParseRule("total-student-enrollments-states.csv", "ANSI", "State", "Total Students [State] ", "0400000US"))
    transformer.transform()

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
    elif(args.p=="elsi/expenditures"):
        parse_elsi_expenditures("data/"+args.p)
    elif(args.p=="elsi/enrollments"):
        parse_elsi_enrollments("data/"+args.p)

        """
        Add other data sources here. Stick to the source/variable naming convention.
        """
    else:
        print "unknown cat/subcat data source specified"

