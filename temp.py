li = [1, 2, 3, 4, 5]
for item in li:
    match item:
        case 1:
            print("11")
        case 2:
            print("22")
        case 3:
            print("33")
        case _:
            print("end")
