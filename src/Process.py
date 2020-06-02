class Process:
    def __init__(self, id: int, name: str, duration: int):
        """
        Constructor method which is called when an object is created.

        :param id: Process ID
        :param name: Process name
        :param duration: Duration of the process
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
        # Empty list variables, compare with Java ArrayList
        self.predecessor = []
        self.successor = []
        # Height level of the process
        self.gui_height = None

    def get_id(self):
        """
        Getter method.

        :return: Process ID
        """
        return self.id

    def set_id(self, new_id: int):
        """
        Setter method.

        :param new_id: Int to set variable to.
        :return: None
        """
        self.id = new_id

    def get_name(self):
        """
        Getter method.

        :return: Process name
        """
        return self.name

    def set_name(self, new_name: str):
        """
        Setter method.

        :param new_name: String to set variable to.
        :return: None
        """
        self.name = new_name

    def get_dauer(self):
        """
        Getter method.

        :return: Process duration
        """
        return self.duration

    def set_dauer(self, new_duration: int):
        """
        Setter method.

        :param new_duration: Int to set variable to.
        :return: None
        """
        self.duration = new_duration

    def calc_fez(self):
        """
        Calculate the FEZ of a process.
        If the process is the start process the value equals the duration.

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
        Calculate the FAZ of a process.
        If the process is the start process the value equal 0.

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
        Calculate the SAZ of a process.
        The SEZ is required for this calculation.

        :return: none
        """
        if self.sez is not None:
            self.saz = self.sez - self.duration
        else:
            raise RuntimeError("SEZ has not been calculated for this object yet.")

    def calc_sez(self):
        """
        Calculate the SEZ of a process.
        If the process is the end process the value equals the FEZ.

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
        Determine if the given process is part of the "critical path".

        :return: bool; depending on if the process is part of the "critical path"
        """
        if self.gp == 0 and target.gp == 0:
            return True
        else:
            return False

    def add_predecessor(self, process):
        """
        Adds a process to the list of following processes.

        :param process: Process to be added
        :return: none
        """
        self.predecessor.append(process)

    def add_successor(self, process):
        """
        Adds a process to the list of previous processes.

        :param process: Process to be added
        :return: none
        """
        self.successor.append(process)

    def add_successor_and_predecessor(self, process):
        """
        Adds a process A to the list of following processes of process B.
        Afterwards add process B to the list of previous processes of process A.

        If the process has already been added no changes occur.

        :param process: Process to add as a following process.
        :return: none
        """
        if process not in self.successor:
            self.successor.append(process)
            process.add_predecessor(self)

    def is_predecessor(self, process):
        """
        Check if a process is part of another processes predecessors.

        :param process: Process to check if it's a predecessor
        :return: bool, whether or not the process is a predecessor
        """
        if process.id in self.predecessor:
            return True
        else:
            return False

    def is_successor(self, process):
        """
        Check if aprocess is part of another processes successors.

        :param process: Process to check if it's a successor
        :return: bool, whether or not the process is a successor
        """
        if process.id in self.successor:
            return True
        else:
            return False

    def is_start_process(self):
        """
        Check if a process is the start process.

        :return: bool, whether or not the process is the starting process.
        """
        if len(self.predecessor) == 0:
            return True
        else:
            return False

    def is_end_process(self):
        """
        Check if a process is the ending process.

        :return: bool, whether ot not the process is the ending process.
        """
        if len(self.successor) == 0:
            return True
        else:
            return False
