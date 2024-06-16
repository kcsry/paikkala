import csv

xxx = """
Permanto,Permanto,1,1,16
Permanto,Permanto,2,17,44
Permanto,Permanto,3,45,73
Permanto,Permanto,4,74,102
Permanto,Permanto,5,103,133
Permanto,Permanto,6,134,166
Permanto,Permanto,7,167,195
Permanto,Permanto,8,196,220
Permanto,Permanto,9,221,244
Permanto,Permanto,10,245,266
Permanto,Permanto,11,267,287
Permanto,Permanto,12,288,307
Permanto,Permanto,13,308,325
Permanto,Permanto,14,326,343
Permanto,Permanto,15,344,359
Permanto,Permanto,16,360,371
Permanto,Permanto,17,372,378
Permanto,Permanto,18,379,382
Permanto,Permanto,19,383,440
Permanto,Permanto,20,441,496
Permanto,Permanto,21,497,554
Permanto,Permanto,22,555,609
Permanto,Permanto,23,610,650
""".strip()

rows = list(csv.reader(xxx.splitlines()))

for floor, zone, row, start, end in rows:
    left_start = int(start)
    right_end = int(end)
    left_end = int(round((left_start + right_end) / 2, 0))
    right_start = left_end + 1
    print(f'{floor},{zone},{left_start},{left_end},Vasen')
    print(f'{floor},{zone},{right_start},{right_end},Oikea')

print(rows)
