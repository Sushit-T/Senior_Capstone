"""
Filename:   globals.py
Author:     Jacob Kucinski and Kelsey Marquez
Date:       8/8/24
Description:
"""

"""
LENGTH OF MESSAGE
"""
HEADER_BYTES    = 3
PAYLOAD_BYTES   = 8
MSG_BYTES = HEADER_BYTES + PAYLOAD_BYTES

### USB MESSAGE FORMAT
# -header-
ID_BYTE      = 0    # MSG ID -> 1 byte
CMD_BYTE     = 1    # CMD    -> 1 byte
STAT_BYTE    = 2    # STATUS -> 1 byte

"""
TUNNELING APPROACH GLOBAL VARIABLES
"""
VPIEZO_APPROACH_MAX     = 5.0       # maximum vpiezo value (v)
VPIEZO_APPROACH_MIN     = 0.0       # minimum vpiezo value (v)
PIEZO_EXTN_RATIO        = 20.0      # vpiezo extension ration (nm per volt)
PIEZO_CODE_RATIO        = 6553.6    # vpiezo code ratio
POS_TOLERANCE           = 0.1       # positional tolerance (nm)
APPROACH_STEP_SIZE_NM   = 0.1       # tunneling approach step size (nm)
#FREQ_RES                = 150.0     # frequency (hz)
TUNNELING_SAMPLE_SIZE   = 4         # tunneling approach sample size

"""
FEEDBACK CONTROLLER GLOBAL VARIABLES
"""
CONTROLLER_MIN_CURR                 = 0.1       # minimum current (nA)
CONTROLLER_CONST_STEP_SZ_NM         = 0.1       # constant step size (nm)    
CONTROLLER_DC_GAIN                  = 0.0001    # DC gain

"""
CAP APPROACH GLOBAL VARIABLES
"""
REGION_1_CAP            = 90.0  # fF
STP_SZ_R1               = 10000.0 
CAP_APPROACH_AMPL       = 1
CAP_APPROACH_FREQ       = 1000
DELAY_LINE_LEN          = 50
CRIT_CAP_SLOPE          = 0.0223
CAP_APPROACH_NUM_STEPS  = 10
FFT_AVG_LENGTH          = 5
DIFF_AVG_BUF_LEN        = 5

"""
VOLTAGE GLOBAL VARIABLES
"""
# Voltage sample bias valid range
VBIAS_MIN   = -10.0
VBIAS_MAX   = 10.0

# Voltage piezo valid range
VPIEZO_MIN  = 0.0
VPIEZO_MAX  = 10.0

# Volts per step for voltage piezo
IZ_VOLTS_PER_STEP_MIN = 0.0002
IV_VOLTS_PER_STEP_MIN = 0.0004

# Voltage piezo delta
VPIEZO_DELTA_MIN = 0.0002

"""
NUMBER OF SETPOINTS AND SAMPLE SIZE GLOBAL VARIABLES
"""
SAMPLE_SIZE_MIN = 1
SAMPLE_SIZE_MAX = 1024

NUM_SETPOINTS_MIN = 0


"""
MESSAGE COMMAND GLOBAL VARIABLES
"""
# The message representation of different message types
MSG_A = 0X0A
MSG_B = 0X0B
MSG_C = 0X0C
MSG_D = 0X0D
MSG_E = 0X0E
MSG_F = 0X0F
MSG_X = 0x58

# The message representation of different step sizes
FULL_STEP       = 0x00
HALF_STEP       = 0x01
QUARTER_STEP    = 0x02
EIGHTH_STEP     = 0x03

# The distance in nanometers of the step sizes
FULL_STEP_DISTANCE      = 0.008
HALF_STEP_DISTANCE      = 0.004
QUARTER_STEP_DISTANCE   = 0.002
EIGHTH_STEP_DISTANCE    = 0.001

# Amount to increase the step size by
INC_FULL  = 1
INC_HALF  = 0.5
INC_QUART = 0.25
INC_EIGHT = 0.125

# Direction the stepper motor is moving
DIR_UP      = 0x00
DIR_DOWN    = 0x01

# Number of steps to move the stepper motor by with user adjustment
NUM_STEPS = 1

"""
TIMING AND MESSAGE CHECKING
"""
# Time
TIMEOUT         = 10.0
ONE_SECOND      = 1.0
HALF_SECOND     = 0.5
TENTH_SECOND    = 0.1

# Attempts
MAX_ATTEMPTS    = 10
SWEEP_MAX_ATTEMPTS  = 10

# Graph rollover
ROLLOVER_GRAPH_TIME = 10.0

"""
BAUD RATE
"""
BAUDRATE = 460800