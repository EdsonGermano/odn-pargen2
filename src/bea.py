import csv
import os

def parse_bea_personal_income(dir):

    def parse_fips(row, file_name):
        if int(row['GeoFips'])==0:
            return '0100000US', 'nation', row['GeoName']
        elif file_name=='states_rpi.csv':
            return "0400000US"+row['GeoFips'][:2], 'state', row['GeoName']
        elif file_name=='metros_rpi.csv' and row['GeoFips']!="00999": #ignore United States nonmetro
            return "310M200US"+row['GeoFips'], 'msa', row['GeoName'].split(" (Metro")[0]
        return None, None, None

    fieldnames = ['id', 'name', 'type', 'year', 'variable', 'value']
    out_file = 'transformed-rpi.csv'

    print "writing to " + out_file
    with open(out_file, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for file_name in os.listdir(dir):
            file_path = dir + "/" + file_name
            print "parsing: " + file_path

            input_file = csv.DictReader(open(file_path))

            i = 0
            for row in input_file:
                i += 1
                #print row

                try:
                    fips, type, name = parse_fips(row, file_name)
                    if fips==None:
                        print "skipping: " + row
                        continue

                    for y in ["2008","2009","2010","2011","2012","2013","2014"]:
                        writer.writerow(
                            {'id': fips, 'name': name, 'type': type, 'year': y,
                             'variable': 'personal_income', 'value': row[y]})
                except:
                    print "skipping failed row %d\n" % i
                    print row

        print "done"