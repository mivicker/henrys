import re
path = input('Which template? \n')

pattern = r'(?<=\{\{) [a-z._]*'
with open(path) as f:
    hits = re.findall(pattern, f.read())
    for hit in hits:
        print(hit)