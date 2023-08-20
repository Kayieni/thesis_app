import re 
import csv

# initiate variables
# i need global because of scopes
text = ""
global num, code, name, pap, moun, eq, mmax

# the txt file contains the copy pasted table from the thesis of Vamvakaris
with open("./cords.txt", encoding="utf8") as f:
    contents = f.read()
    text=contents

rows = text.split('\n')

# define the header of the csv that will be created afterwards
fields = ["id", "code", "name", "lat", "long", "pap", "moun", "eq", "mmax"]

# create the csv, with the defined header
with open('cords.csv', 'w', newline='\n') as file: 
    writer = csv.DictWriter(file, fieldnames = fields)
    writer.writeheader()

    for row in rows:
        row = row.strip()
        if not row:
            continue
            
        columns = []

    # First type of row: starts with a number, followed by the area code and a string, then decimal numbers  
    # e.g.               1,              T-A1,               W. Montenegro,                            42.50,        17.90,         7.2,            7.6,            7.1,            7.2
    #                   ____   ____________________    __________________________________________     ________     ________     ___________     ___________     ___________     ___________
        if re.match(r'^(\d+)\s+([A-Z][.-]?[A-Z]\d+)\s+([A-Za-z]+\.?\s?\S+\s?\S*\s?\d*\s?\(?.*?\)?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\-|\d+\.\d+)\s+(\-|\d+\.\d+)\s+(\-|\d+\.\d+)\s+(\-|\d+\.\d+)$', row):
            # columns = re.split(r'\s+', row)
            match = re.match(r'^(\d+)\s([A-Z][.-]?[A-Z]\d+)\s+([A-Za-z]+\.?\s?\S+\s?\S*\s?\d*\s?\(?.*?\)?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\-|\d+\.\d+)\s+(\-|\d+\.\d+)\s+(\-|\d+\.\d+)\s+(\-|\d+\.\d+)$', row)
            columns = [match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6), match.group(7), match.group(8), match.group(9)]
            num = match.group(1)
            code = match.group(2)
            name = match.group(3)
            pap = match.group(6)
            moun = match.group(7)
            eq = match.group(8)
            mmax = match.group(9)
            print('______________________________________________________________________________________________________________________________________\n')

        # Second type of row: starts with a Greek letter, followed by a string, then two decimal numbers
        elif re.match(r'^([Α-Ωα-ω]+\.?\s?\S+\s?\S*\s?\d*\s?\(?.*?\)?)\s+(\d+\.\d+)\s+(\d+\.\d+)$', row):
            match = re.match(r'^([Α-Ωα-ω]+\.?\s?\S+\s?\S*\s?\d*\s?\(?.*?\)?)\s+([\d\.]+)\s+([\d\.]+)$', row)
            columns = ["", code,name, match.group(2), match.group(3),pap,moun,eq,mmax]
        
        # Third type of row: starts with two decimal numbers, followed by two more decimal numbers
        elif re.match(r'^[\d\.]+\s+[\d\.]+\s*$', row):
            match = re.match(r'^([\d\.]+)\s+([\d\.]+)\s*$', row)
            columns = ["", code,name, match.group(1), match.group(2),pap,moun,eq,mmax]
        
        # Print the columns separated by vertical and tabs to be more recognizable
        print('\t|\t'.join(columns))

        # write the results to the csv
        writer = csv.writer(file, delimiter=',')
        writer.writerow(columns)
        # for easier access and edit during the insertion on the mysql database, we only keep the "code" in the 2nd and 3d type rows so we know which area to connect the coordinates with.
        

# i could do it all here without creating any csv.

            
