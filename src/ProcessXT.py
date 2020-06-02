from Process import Process


class ProcessXT(Process):
    def calc_gp(self):
        """
        Calculate the GP of a process.

        :return: None
        """
        self.gp = self.saz - self.faz

    def calc_fp(self):
        """
        Calculate the FP of a process.
        If the process has no successors the FP equals 0.

        :return: None
        """
        if len(self.successor) == 0:
            self.fp = 0
        else:
            current_max = 0
            for succ_element in self.successor:
                if succ_element.faz > current_max:
                    current_max = succ_element.faz
            self.fp = current_max - self.fez
