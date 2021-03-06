from ProcessXT import ProcessXT
"""
# Prozesse werden erstellt
proc1 = ProcessXT(1, "A", 2)
proc2 = ProcessXT(2, "B", 4)
proc3 = ProcessXT(3, "C", 3)
proc4 = ProcessXT(4, "D", 2)
proc5 = ProcessXT(5, "E", 1)
proc6 = ProcessXT(6, "F", 4)
proc7 = ProcessXT(7, "G", 5)

# Nachfolger und Vorgaenger werden angegeben
proc1.add_successor_and_predecessor(proc2)
proc2.add_successor_and_predecessor(proc3)
proc2.add_successor_and_predecessor(proc4)
proc3.add_successor_and_predecessor(proc5)
proc3.add_successor_and_predecessor(proc6)
proc4.add_successor_and_predecessor(proc5)
proc5.add_successor_and_predecessor(proc7)
proc6.add_successor_and_predecessor(proc7)

# Liste aller Prozesse wird erstellt
list_of_proc = [proc1, proc2, proc3, proc4, proc5, proc6, proc7]
"""

proc0 = ProcessXT(0, "Start", 0)
proc1 = ProcessXT(1, "A1", 1)
proc2 = ProcessXT(2, "B1", 1)
proc3 = ProcessXT(3, "B2", 3)
proc4 = ProcessXT(4, "End", 0)

proc0.add_successor_and_predecessor(proc1)
proc1.add_successor_and_predecessor(proc2)
proc1.add_successor_and_predecessor(proc3)
proc2.add_successor_and_predecessor(proc4)
proc3.add_successor_and_predecessor(proc4)

list_of_proc = [proc0, proc1, proc2, proc3, proc4]

# faz    fez
# saz    sez

# Vorwaertsterminierung
for element in list_of_proc:
    element.calc_faz()
    element.calc_fez()

# Rueckwaertsterminierung
for element in list_of_proc[::-1]:
    element.calc_sez()
    element.calc_saz()

# Pufferberechnung
for element in list_of_proc:
    element.calc_gp()
    element.calc_fp()

print(proc3.is_critical())
print()
