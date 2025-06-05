"""
GolfBot-EV3 konfigurationsfil
Samler alle porte, hastigheder, vinkler, tider og projektkonstanter ét sted.
Opdater denne fil for at ændre robotadfærd på tværs af hele projektet.
"""

from pybricks.parameters import Port, Color

# -------------------------------
# PORTDEFINITIONER (motorer & sensorer)
# -------------------------------

# Motorporte
PORT_LEFT_MOTOR = Port.A      # Venstre hjulmotor
PORT_RIGHT_MOTOR = Port.D     # Højre hjulmotor
PORT_GATE_MOTOR = Port.C      # Port/gate-motor (foran)
PORT_PUSH_MOTOR = Port.B      # Boldskubber-motor (bagud)

# Sensorporte
PORT_COLOR_SENSOR = Port.S1
PORT_TOUCH_SENSOR = Port.S2
PORT_ULTRASONIC_SENSOR = Port.S3
PORT_GYRO_SENSOR = Port.S4

# -------------------------------
# STANDARD MOTORHASTIGHEDER (deg/s)
# -------------------------------

DRIVE_SPEED = 300              # Standard kørehastighed
TURN_SPEED = 150               # Standard drejehastighed

GATE_MOTOR_SPEED = 150         # Portmotor
PUSH_MOTOR_SPEED = 500         # Boldskubber

# -------------------------------
# VINKLER & AFSTANDE (grader, mm)
# -------------------------------

GATE_OPEN_ANGLE = 35           # Port åbning (grader)
GATE_CLOSE_ANGLE = -35         # Port lukning (grader)

PUSH_OUT_ANGLE = 40            # Boldskub frem (grader)
PUSH_RETURN_ANGLE = 0          # Tilbage til start

# -------------------------------
# TIDER (ms)
# -------------------------------

GATE_WAIT_TIME = 1500
PUSH_WAIT_TIME = 500
GENERAL_WAIT_TIME = 200

# -------------------------------
# BOLD & ROBOT KONFIGURATION
# -------------------------------

BALL_COUNT_MAX = 6             # Lagerkapacitet
WHEEL_DIAMETER_MM = 55.5
AXLE_TRACK_MM = 104

# -------------------------------
# VISION-MODUL (kommende)
# -------------------------------

VISION_CAMERA_ID = 0
VISION_FRAME_WIDTH = 640
VISION_FRAME_HEIGHT = 480
VISION_BALL_COLOR = Color.WHITE    # Brug Color.ORANGE for VIP-bold

# -------------------------------
# NAVIGATION-MODUL (kommende)
# -------------------------------

NAV_GRID_SIZE = 20
NAV_START_POSITION = (0, 0)
NAV_GOAL_POSITION = (1000, 0)

# -------------------------------
# ØVRIGE KONSTANTER
# -------------------------------

DEBUG = True

# -------------------------------
# SLUT PÅ KONFIGURATION
# -------------------------------
