# Open and read the file
with open('report-gradedistribution-2024-2025fall.txt', 'r') as file:
    content = file.read()
    char_count = len(content)

print(f"Total characters: {char_count}")
print(f"Total tokens: {char_count/4}")