message = "abc"
print(message.rjust(10, "_")+"end")  # 向右挪动10个字符,默认为空格 _______abcend
print(message.ljust(15, "*")+"end")  # 向左挪动15个字符,默认为空格 abc************end
print(message.center(20, "="))  # ========abc=========
