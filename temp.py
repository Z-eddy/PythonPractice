li = [1, 2, 3, 4, 5, 6]
liTemp = []
for item in li:
    if item%2 == 0:
        liTemp.append(item+20)
        print("item%2==0")
    elif item//3 == 0:
        liTemp.append(item+30)
        print("item//3==0")
    else:
        print("pass")
        pass

print(liTemp)
