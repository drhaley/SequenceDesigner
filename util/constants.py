"""for global enumerations and constants"""

###############################
#keys used in settings file
SETTINGS_FILENAME = "settings_file"
TEMPERATURE = "temperature"
ORACLE = "oracle"
SEQUENCE_ITERATOR = "sequence_iterator"
ARBITER = "arbiter"
###############################

###############################
#internal parameters for which a default must be defined
MAX_FITNESS = 100   #used as a learning parameter to give feedback on considered sequences
###############################

###############################
#tuning parameters for use in considering sequence viability
#TODO: accept tuning parameters as arguments in related functions or pull from parameter file
MIN_AFFINITY_TO_SELF = 12.0
MAX_AFFINITY_TO_OTHER_SINGLE = 5.0
MAX_AFFINITY_TO_OTHER_PAIR = 5.0
###############################

###############################
# #TODO: connect verbosity and max_considered to command-line arguments or to the parameter file
VERBOSE = False
MAX_SEQUENCES_CONSIDERED = 1000
###############################
