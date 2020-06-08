message="     hello 'world'\t      "
#生成临时亮而非更改自身
tempDelRightMes=message.rstrip()#去掉右边空白
tempDelLeftMes=message.lstrip()#去掉左边空白
tempDelWhiteMes=message.strip()#去掉两边空白
print(tempDelRightMes)
print(tempDelLeftMes)
print(tempDelWhiteMes)