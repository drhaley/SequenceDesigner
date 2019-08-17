import abc   #abstract classes

class AbstractOracle(abc.ABC):
    @abc.abstractmethod
    def self_affinity(sequence, temperature):
        pass

    @abc.abstractmethod
    def binding_affinity(sequence1, sequence2, temperature):
        pass


class DebugOracle(AbstractOracle):
    #for testing purposes only; do not use for design purposes
    
    __LOOPOUT_SIZE = 4

    def self_affinity(self,
            sequence, temperature):

        if len(sequence) < self.__LOOPOUT_SIZE + 2:
            return 0.0
        else:
            possible_loopout_positions = range(1,len(sequence)-self.__LOOPOUT_SIZE-1)
            return \
                min([
                    self.binding_affinity(
                        sequence[:loopout_start],
                        sequence[loopout_start+self.__LOOPOUT_SIZE:],
                        temperature
                    )
                    for loopout_start in possible_loopout_positions
                ])

    def binding_affinity(self, 
            sequence1, sequence2, temperature):

        return \
            min([
                sum([
                    self.__base_pair_energy(
                        sequence1[offset1+i],sequence2[-(offset2+i)], temperature
                    )
                    for i in range(
                        min([len(sequence1)-offset1, len(sequence2)-offset2])
                    )
                ])
                for offset1 in range(len(sequence1))
                for offset2 in range(len(sequence2))
            ])

    def __base_pair_energy(self,
            base1, base2, temperature):

        base_pair = {base1.upper(),base2.upper()}
        if {'A','T'}.issubset(base_pair):
            return -50.0/temperature
        elif {'C','G'}.issubset(base_pair):
            return -200.0/temperature
        else:
            return 0.0
