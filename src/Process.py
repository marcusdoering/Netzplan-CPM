class Process:
    def __init__(self, id: int, name: str, duration: int):
        """
        Constructor-Funktion, welche beim Erstellen eines Objekts aufgerufen wird.

        :param id: Die ID eines Prozesses
        :param name: Name eines Prozesses
        :param duration: Dauer bzw Laenge eines Prozesses
        """
        self.faz = None
        self.fez = None
        self.saz = None
        self.sez = None
        self.id = id
        self.name = name
        self.gp = None
        self.fp = None
        self.duration = duration
        # Leere List-Variablen, vergleichbar mit ArrayLists in Java
        self.predecessor = []
        self.successor = []

    def get_id(self):
        """
        Getter-Methode

        :return: Die ID eines Prozesses
        """
        return self.id

    def set_id(self, new_id: int):
        self.id = new_id

    def get_name(self):
        return self.name

    def set_name(self, new_name: str):
        self.name = new_name

    def get_dauer(self):
        return self.duration

    def set_dauer(self, new_duration: int):
        self.duration = new_duration

    def calc_fez(self):
        """
        Berechnet den FEZ des Prozesses oder gibt einen angepassten Wert zurueck,
        falls es sich um den Startprozess handelt

        :return: none
        """
        if self.is_start_process():
            self.fez = self.duration
        else:
            self.fez = self.faz + self.duration

    def calc_faz(self):
        """
        Berechnet den FAZ des Prozesses oder gibt 0 zurueck, falls es sich um
        den Startprozess handelt

        :return: none
        """
        if self.is_start_process():
            self.faz = 0
        else:
            current_max = 0
            for pre_element in self.predecessor:
                if pre_element.fez > current_max:
                    current_max = pre_element.fez
            self.faz = current_max

    def calc_saz(self):
        self.saz = self.sez - self.duration

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
        """
        Gibt an, ob ein Prozess zum "kritischen Pfad" gehoert

        :return: bool; je nachdem ob Prozess zum "kritischen Pfad" gehoert
        """
        if self.gp == 0:
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
