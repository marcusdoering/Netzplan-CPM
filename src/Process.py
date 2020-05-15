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
        self.duration = duration
        self.gp = None
        self.fp = None
        # Leere List-Variablen, vergleichbar mit ArrayLists in Java
        self.predecessor = []
        self.successor = []
        # gui height
        self.gui_height = None

    def get_id(self):
        """
        Getter-Methode.

        :return: Die ID eines Prozesses
        """
        return self.id

    def set_id(self, new_id: int):
        self.id = new_id

    def get_name(self):
        """
        Getter-Methode.

        :return: Den Namen eines Prozesses
        """
        return self.name

    def set_name(self, new_name: str):
        self.name = new_name

    def get_dauer(self):
        """
        Getter-Methode.

        :return: Die Dauer eines Prozesses
        """
        return self.duration

    def set_dauer(self, new_duration: int):
        self.duration = new_duration

    def calc_fez(self):
        """
        Berechnet den FEZ des Prozesses oder gibt einen angepassten Wert zurueck,
        falls es sich um den Startprozess handelt.

        :return: none
        """
        if self.is_start_process():
            self.fez = self.duration
        elif self.faz is not None:
            self.fez = self.faz + self.duration
        else:
            raise RuntimeError("FAZ has not been calculated for this object yet.")

    def calc_faz(self):
        """
        Berechnet den FAZ des Prozesses oder gibt 0 zurueck, falls es sich um
        den Startprozess handelt.

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
        """
        Berechnet den SAZ des Prozesses. Der SEZ muss dazu gegeben sein.

        :return: none
        """
        if self.sez is not None:
            self.saz = self.sez - self.duration
        else:
            raise RuntimeError("SEZ has not been calculated for this object yet.")

    def calc_sez(self):
        """
        Berechnet den SEZ des Prozesses or gibt den FEZ zurueck, wenn es sich um
        den Endprozess handelt.

        :return: none
        """
        if self.is_end_process():
            if self.fez is not None:
                self.sez = self.fez
            else:
                raise RuntimeError("FEZ has not been calculated for this object yet.")
        else:
            current_min = 9999
            for succ_element in self.successor:
                if succ_element.saz < current_min:
                    current_min = succ_element.saz
            self.sez = current_min

    def is_critical(self, target):
        """
        Gibt an, ob ein Prozess zum "kritischen Pfad" gehoert.

        :return: bool; je nachdem ob Prozess zum "kritischen Pfad" gehoert
        """
        if self.gp == 0 and target.gp == 0:
            return True
        else:
            return False

    def add_predecessor(self, process):
        """
        Fuegt einen Prozess der Liste der vorhergehenden Prozesse hinzu.

        :param process: Prozess, welcher der Liste hinzugefuegt wird
        :return: none
        """
        self.predecessor.append(process)

    def add_successor(self, process):
        """
        Fuegt eine Prozess der Liste der nachfolgenden Prozesse hinzu.

        :param process: Prozess, welcher der Liste hinzugefuegt wird
        :return: none
        """
        self.successor.append(process)

    def add_successor_and_predecessor(self, process):
        """
        Fuegt einen Prozess A der Liste der nachfolgenden Prozesse von Prozess B hinzu.
        Prozess B wird danach der Liste der vorhergehenden Prozesse von Prozess A hinzugefuegt.

        Wurde der Prozess bereits hinzugefuegt, so wird keine Aenderung vorgenommen.

        :param process: Prozess, welcher als Nachfolger eingetragen wird
        :return: none
        """
        if process not in self.successor:
            self.successor.append(process)
            process.add_predecessor(self)

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
