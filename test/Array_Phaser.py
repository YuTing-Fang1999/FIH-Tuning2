class Array_Phaser():
    def __init__(self, text) -> None:
        self.text = text
        self.pos_arr = []
        self.phase = []
    
        cnt = 0
        i = 0
        while i<len(text):
            # comment
            if text[i]=='/' and i+1<len(text):

                if text[i+1]=='/':
                    while i<len(text) and text[i]!='\n':
                        i+=1

                if text[i+1]=='*':
                    i+=2
                    while i+1<len(text) and not (text[i]=='*' and text[i+1]=='/'):
                        i+=1
                    i+=2

            else:                

                if  self.is_char(text[i]) and cnt==0:
                    self.pos_arr.append([i])
                    while i<len(text) and self.is_char(text[i]):
                        i+=1
                    self.pos_arr[-1].append(i)
                
                else:

                    if text[i]=='{':
                        if cnt==0:
                            self.pos_arr.append([i+1])
                        cnt+=1
                        
                    if text[i]=='}':
                        cnt-=1
                        if cnt==0:
                            self.pos_arr[-1].append(i)
                            while i<len(text) and text[i]!=',':
                                i+=1

            i+=1
        
    def is_char(self, c):
        return c not in ['  ',' ',',','\n','{','}']

        # print(self.pos_arr)
    def get(self, idx):
        if len(self.phase)==0: self.phase = [ Array_Phaser(self.text[p[0]:p[1]]) for p in self.pos_arr ]
        if len(self.phase)==0: return None
        return self.phase[idx]

    def reconstruct(self):
        dif = 0
        for i in range(len(self.phase)):
            new_phase = self.phase[i].reconstruct()
            start = self.pos_arr[i][0]
            end = self.pos_arr[i][1]
            ori_len = end-start
            new_len = len(new_phase)
            self.text[start+dif:end+dif]=new_phase
            self.pos_arr[i] = [start+dif, start+dif+new_len]
            dif += (new_len-ori_len)
            # print(''.join(self.text))

        return self.text



path = 'chromatix_hi556_j3_main_snapshot.h'
with open(path, 'r', encoding='cp1252') as f:
    text = f.read()

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
   // Effect: disable hot bad pixel correction
   // This value represents Upper/Lower bad pixel threshold offset for r/b pixels for T2
   // Default value: 4095.
   // Data range: 0 to 4095
   // Effect: change;  Upper/Lower bad pixel threshold offset for r/b pixels for T2
   /******************************************************************************/
12,
/* Chromatix App Version */
{
    6, /* Major */
    16, /* Minor */
    6, /* Revision */
    0, /* Build */
},
11
"""
arr_phaser = Array_Phaser(list(text))
# arr_phaser.get(1).get(3).get(5).text = "1234"
# print(''.join(arr_phaser.get(1).reconstruct()[:1000]))

abf_node = arr_phaser.get(1).get(3).get(5)
trigger_idx=0

for i in range(len(abf_node.get(trigger_idx).get(0).pos_arr)):
    abf_node.get(trigger_idx).get(0).get(i).text = str(i)

path = 'chromatix_hi556_j3_main_snapshot_modify.h'
with open(path, 'w', encoding='cp1252') as f:
    f.write(''.join(arr_phaser.reconstruct()))



# ABF
# FILE: 
