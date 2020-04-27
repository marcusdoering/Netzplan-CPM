class Process:
    def __init__(self, id, name, dauer):
        self.faz = None
        self.fez = None
        self.saz = None
        self.sez = None
        self.id = id
        self.name = name
        self.gp = None
        self.fp = None
        self.dauer = dauer
        self.predecessor = []
        self.successor = []

    def get_id(self):
        return self.id

    def set_id(self, new_id: int):
        self.id = new_id

    def get_name(self):
        return self.name

    def set_name(self, new_name: str):
        self.name = new_name

    def get_dauer(self):
        return self.dauer

    def set_dauer(self, new_dauer: int):
        self.dauer = new_dauer

    def calc_fez(self):
        if self.is_start_process():
            self.fez = self.dauer
        else:
            self.fez = self.faz + self.dauer

    def calc_faz(self):
        if self.is_start_process():
            self.faz = 0
        else:
            current_max = 0
            for pre_element in self.predecessor:
                if pre_element.fez > current_max:
                    current_max = pre_element.fez
            self.faz = current_max

    def calc_saz(self):
        self.saz = self.sez - self.dauer

    def calc_sez(self):
        if self.is_end_process():
            self.sez = self.fez
        else:
            current_min = 9999
            for succ_element in self.successor:
                if succ_element.saz < current_min:
                    current_min = succ_element.saz
            self.sez = current_min

    def is_critical(self):
        if self.faz == self.saz:
            return True
        else:
            return False

    def add_predecessor(self, process):
        self.predecessor.append(process)

    def add_successor(self, process):
        self.successor.append(process)

    def is_predecessor(self, process):
        if process.id in self.predecessor:
            return True
        else:
            return False

    def is_successor(self, process):
        if process.id in self.successor:
            return True
        else:
            return False

    def is_start_process(self):
        if len(self.predecessor) == 0:
            return True
        else:
            return False

    def is_end_process(self):
        if len(self.successor) == 0:
            return True
        else:
            return False
