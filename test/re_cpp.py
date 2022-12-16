s = """
/* Header Version Info */
{
   0x0310, /* Chromatix Version */
   1, /* Revision */
   /* Chromatix App Version */
   {
      6, /* Major */
      16, /* Minor */
      6, /* Revision */
      0, /* Build */
   },
   HEADER_DEFAULT, /* Header Type */
   0, /* Is Compressed */
   0, /* Is Mono */
   0, /* Is Video */
   0, /* Reserved Align */
   MODE_UNKNOWN, /* Chromatix Mode */
   0, /* Target ID */
   0, /* Chromatix ID */
   /* Reserved */
   {
      0, 0, 0, 0
   }
},
"""

import re
s = '{ 0 },'
p = re.compile('\{(.)*\}')
# print(p.match())

# import re
print(re.sub(p, "+", s))