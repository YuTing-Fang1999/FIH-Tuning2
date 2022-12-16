s = """
/* Header Version Info */
{
   0x0310, /* Chromatix Version */
   1, /* Revision */
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
/* Chromatix App Version */
{
    6, /* Major */
    16, /* Minor */
    6, /* Revision */
    0, /* Build */
},
"""
s = list(s)
pos_arr = []
cnt = 0
nth = 0
idx=0
for i, c in enumerate(s):
    if c=='{':
        if cnt==0 and idx==nth:
            pos_arr.append(i+1)
        cnt+=1
        
    if c=='}':
        cnt-=1
        if cnt==0 and idx==nth:
            pos_arr.append(i)

        if cnt==0:
            nth+=1
            

s = s[pos_arr[0]:pos_arr[1]]
print(''.join(s))
