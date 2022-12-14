from io import StringIO
import sys


example = 'hello 123'

# 👇️ remove call to print() to assign to a variable
my_str = str(example)
print(my_str) # 👉️ hello 123

# -------------------------------------

# ✅ Redirect print() output to a variable

buffer = StringIO()
sys.stdout = buffer

print('This will be stored in the print_output variable')
print_output = buffer.getvalue()

# 👇️ restore stdout to default for print()
sys.stdout = sys.__stdout__

# 👇️ -> This will be stored in the print_output variable
print('->', print_output)
