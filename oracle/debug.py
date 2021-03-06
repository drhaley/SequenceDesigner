from oracle.abstract import AbstractOracle

class Oracle(AbstractOracle):
    #for testing purposes only; do not use for design purposes

    def __init__(self, *args):
        print("*"*80 + "\nWARNING: Instantiated Debug Oracle, do not deploy!\n" + "*"*80)
        super().__init__(*args)
    
    __LOOPOUT_SIZE = 4

    def self_affinity(self, sequence):

        if len(sequence) < self.__LOOPOUT_SIZE + 2:
            return 0.0
        else:
            possible_loopout_positions = range(1,len(sequence)-self.__LOOPOUT_SIZE-1)
            return \
                max([
                    self.binding_affinity(
                        sequence[:loopout_start],
                        sequence[loopout_start+self.__LOOPOUT_SIZE:]
                    )
                    for loopout_start in possible_loopout_positions
                ])

    def binding_affinity(self, 
            sequence1, sequence2):

        return \
            max([
                sum([
                    self._base_pair_affinity(
                        sequence1[offset1+i],sequence2[-(offset2+i)]
                    )
                    for i in range(
                        min([len(sequence1)-offset1, len(sequence2)-offset2])
                    )
                ])
                for offset1 in range(len(sequence1))
                for offset2 in range(len(sequence2))
            ])

    def _base_pair_affinity(self,
            base1, base2):

        base_pair = {base1.upper(),base2.upper()}
        if {'A','T'}.issubset(base_pair):
            return 50.0/self._temperature
        elif {'C','G'}.issubset(base_pair):
            return 200.0/self._temperature
        else:
            return 0.0
