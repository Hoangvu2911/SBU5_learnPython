import re

text = "Hello, my name 31 is John and my email is john@example.com 123422 32"
phone_number = "Here is my phone number: +84 234 321 345 please call me"

pattern_mail = r"[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+"
pattern_phone = r"\+[0-9]{1,3} [0-9]{3} [0-9]{3} [0-9]{3}"

matches = re.findall(pattern_mail, text)
matches_phone = re.findall(pattern_phone, phone_number)

print(matches)
print(matches_phone)
