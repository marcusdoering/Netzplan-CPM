from src.Process import Process

proc1 = Process(1, "Hallo", 5)
proc2 = Process(2, "Welt", 3)
proc3 = Process(3, "Drei", 4)

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
proc1.faz = 0
for element in [proc1, proc2, proc3]:
    # get fez
    element.fez = element.faz + element.dauer
    # get faz
    for succ_element in element.successor:
        current_max = 0
        # iterate over all pre of succ, save the highest fez
        for pre_of_succ_element in succ_element.predecessor:
            if pre_of_succ_element.fez > current_max:
                current_max = pre_of_succ_element.fez
        # highest fez == succ faz
        succ_element.faz = current_max

# ruckwaetrsterminierung
proc3.sez = proc3.fez
for element in [proc1, proc2, proc3][::-1]:
    # get saz
    element.saz = element.sez - element.dauer
    # get sez
    for pre_element in element.predecessor:
        current_min = 9999
        for succ_of_pre_element in pre_element.successor:
            if succ_of_pre_element.saz < current_min:
                current_min = succ_of_pre_element.saz
        pre_element.sez = current_min

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
