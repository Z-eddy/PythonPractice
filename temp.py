message="i have test this."
count={}
for char in message:
    count.setdefault(char,0)
    count[char]+=1

for key,val in count.items():
    print(key,val)