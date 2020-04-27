from src.Process import Process

proc1 = Process(1, "Hallo", 2)
proc2 = Process(2, "Welt", 4)
proc3 = Process(3, "Drei", 3)

proc1.add_successor(proc2)
proc2.add_predecessor(proc1)
proc2.add_successor(proc3)
proc3.add_predecessor(proc2)

# id 1 dauer 5 vorher -
# id 2 dauer 3 vorher 1
# id 3 dauer 4 vorher 2

# faz    fez
# saz    sez

# vorwaertsterminierung
for element in [proc1, proc2, proc3]:
    element.calc_faz()
    element.calc_fez()

for element in [proc1, proc2, proc3][::-1]:
    element.calc_sez()
    element.calc_saz()

# pufferberechnung
for element in [proc1, proc2, proc3]:
    element.gp = element.saz - element.faz
    if len(element.successor) == 0:
        element.fp = 0
    else:
        current_max = 0
        for succ_element in element.successor:
            if succ_element.faz > current_max:
                current_max = succ_element.faz
        element.fp = current_max - element.fez

print()
