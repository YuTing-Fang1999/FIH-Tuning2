path = 'chromatix_hi556_j3_main_snapshot.h'
with open(path, 'r', encoding='cp1252') as f:
    s = "{"+f.read()+"}"

# s = """
# {
#     {
#         6
#     }, /* Major */
#     16, /* Minor */
#     6, /* Revision */
#     0, /* Build */
# }
# """
s = s.replace('{', '[').replace('}',']').replace('/','#').replace('f','')

import ast
x = ast.literal_eval(s)
# print(x)
print(x[0])
# print(str(x).replace('[', '{').replace(']','}'))
