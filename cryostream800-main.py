#    ______                      __
#   / ____/______  ______  _____/ /_________  ____ _____ ____
#  / /   / ___/ / / / __ \\/ ___/ __/ ___/ _ / __ `/ __ `__  /
# / /___/ /  / /_/ / /_/ (__  ) /_/ /  /  __/ /_/ / / / / / /
# \____/_/   \__, /\____/____/\__/_/   \___/\__,_/_/ /_/ /_/
#           /____/      by BCSB 2023 @ ALS @ Berkeley Labs.")
#                            Cryostream 800 - Beamline 821.")        



# Port Information:
# Port 30303 UDP - Get  Identification Packets. (Not Using)
# Port 30304 UDP - Get  Status Packets.
# Port 30305 UDP - Send Commands.

##########################
### Python 2.7 Edition ###
##########################

#Authors:
#John Taylor, Berkeley National Laboratory (Email: jrtaylor_at_lbl.gov)
#Gabriel Gazolla, Berkeley National Laboratory (Email: gabrielgazolla_at_lbl.gov)

import sys
from cryostream800 import Cryostream800

############
### Main ###
############

#Please, Update Your IP!

BL821_Cryostream800 = Cryostream800(ip="121.223.76.47")

BL821_Cryostream800.terminal_displayMenu()
