import re
rule=re.compile("^[a-z]*.*\d{3}")
message="i have the13456 num 789012abc"
result=rule.search(message)
if(result):
    print(result.group())