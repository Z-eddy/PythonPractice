def reverString(s):
    words=s.split(" ")#按照空格分离word
    words=words[-1::-1]
    outSentence=" "#也可以和下面直接合并
    outSentence = outSentence.join(words)
    return outSentence

s="i like the world"
print(reverString(s))
