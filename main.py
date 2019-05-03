import haltParse
import haltASM
import platform

haltASM.main(haltParse.getTree())
file = open("test.asm", 'w')
file.writelines(haltASM.asmheader)
file.writelines(haltASM.asmdata)
file.writelines(haltASM.asmtext)
file.writelines(haltASM.asmleave)
file.close()
# print(parse2.getTree())
#print(tt.asmtext)
# print("--- compile successful ---")
