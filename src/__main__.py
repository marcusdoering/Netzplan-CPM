from src.ProcessXT import ProcessXT

proc1 = ProcessXT(1, "A", 2)
proc2 = ProcessXT(2, "B", 4)
proc3 = ProcessXT(3, "C", 3)
proc4 = ProcessXT(4, "D", 2)
proc5 = ProcessXT(5, "E", 1)
proc6 = ProcessXT(6, "F", 4)
proc7 = ProcessXT(7, "G", 5)

proc1.add_successor(proc2)
proc2.add_successor(proc3)
proc2.add_successor(proc4)
proc3.add_successor(proc5)
proc3.add_successor(proc6)
proc4.add_successor(proc5)
proc5.add_successor(proc7)
proc6.add_successor(proc7)

proc2.add_predecessor(proc1)
proc3.add_predecessor(proc2)
proc4.add_predecessor(proc2)
proc5.add_predecessor(proc3)
proc5.add_predecessor(proc4)
proc6.add_predecessor(proc3)
proc7.add_predecessor(proc5)
proc7.add_predecessor(proc6)

list_of_proc = [proc1, proc2, proc3, proc4, proc5, proc6, proc7]


# faz    fez
# saz    sez

# vorwaertsterminierung
for element in list_of_proc:
    element.calc_faz()
    element.calc_fez()

# rueckwaertsterminierung
for element in list_of_proc[::-1]:
    element.calc_sez()
    element.calc_saz()

# pufferberechnung
for element in list_of_proc:
    element.calc_gp()
    element.calc_fp()

print()
