li = []
for i in range(2, 10):
    print(i)
    tempItem = {"n0": i+10, "n1": i+11}
    li.append(tempItem)

print(li)

for item in li[:3]:
    item["no"]=88
    item["n1"]=99

print(li)
