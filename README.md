# odn-pargen

OpenDataNetwork.com related ODN source data parsers and dataset generators

1. Add new pargen data into the data directory. Stick to the source/variable naming convention and add README to humans downloading data in the future so the exact instructions can be followed and updated.

2. Add support to parse the kept files in pag.py. Follow the parse_elsi_student_teacher_ratios example.

3. Running:

python pag.py -h

for help

python pag.py -p "elsi/student-teacher-ratios"

for example
