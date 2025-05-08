import os
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

# Page configuration
PAGE_TITLE = "Fridge Monitoring Dashboard"
PAGE_ICON = "🧊"
LAYOUT = "wide"

# AWS configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Timestream database and table configuration
DATABASE_NAME = os.getenv("TIMESTREAM_DATABASE", "RVACF-Timestream-DB")
TABLE_NAME = os.getenv("TIMESTREAM_TABLE", "multi_value")

# Define fridge options and locations
FRIDGE_OPTIONS = {
    #0: "venable-st-fridge",
    #1: "hull-st-fridge",
    #2: "new-kingdom-fridge",
    3: "oakwood-art-fridge",
    #4: "city-church-fridge",
    #5: "studio-23-fridge",
    #6: "fulton-hill-fridge",
    7: "cary-st-fridge",
    #8: "sankofa-fridge",
    #9: "meadowbridge-fridge",
    #10: "6pic-fridge",
    11: "fonticello-fridge",
    #12: "matchbox-mutualaid",
    #13: "main-st-fridge",
    14: "expo-fridge"
}

FRIDGE_LOCATIONS = {
    #'venable-st-fridge': '2025 Venable St, Richmond, VA',
    #'new-kingdom-fridge': '3200 Dill Ave, Richmond, VA',
    #'studio-23-fridge': '109 W 15th St, Richmond, VA',
    #'hull-st-fridge': '2414 Hull St, Richmond, VA',
    #'matchbox-mutualaid': '2919 North Ave, Richmond, VA',
    #'6pic-fridge': '3001 Meadowbridge Rd, Virginia',
    #'meadowbridge-fridge': '3613 Meadowbridge Rd, Richmond, VA',
    'fonticello-fridge': '255 W 27th St, Richmond, VA',
    #'fulton-hill-fridge': '4809 Parker St, Richmond, VA',
    #'city-church-fridge': '4700 Oakleys Ln, Richmond, VA',
    #'sankofa-fridge': '309 Covington Rd, Richmond, VA',
    'oakwood-art-fridge': '917 N 35th St, Richmond, VA',
    'cary-st-fridge': '2913 W Cary St, Richmond, VA',
    #'main-st-fridge': '121 E Main St, Richmond, VA',
    'expo-fridge': '1200 West Broad Street, Richmond, VA'
}

FRIDGE_COORDINATES = {
    #'venable-st-fridge': (37.5395, -77.4259),
    #'new-kingdom-fridge': (37.5601, -77.4368),
    #'studio-23-fridge': (37.5360, -77.4338),
    #'hull-st-fridge': (37.5358, -77.4478),
    #'matchbox-mutualaid': (37.5807, -77.4255),
    #'6pic-fridge': (37.5756, -77.4219),
    #'meadowbridge-fridge': (37.5870, -77.4215),
    'fonticello-fridge': (37.5316, -77.4330),
    #'fulton-hill-fridge': (37.5299, -77.4048),
    #'city-church-fridge': (37.5238, -77.3477),
    #'sankofa-fridge': (37.5659, -77.4666),
    'oakwood-art-fridge': (37.5409, -77.4113),
    'cary-st-fridge': (37.5553, -77.4834),
    #'main-st-fridge': (37.5350, -77.4396),
    'expo-fridge': (37.55227,-77.4526)
}

# Help text for sidebar
HELP_TEXT = """
### Dashboard Controls
- **Navigation:** Switch between Dashboard and Map View
- **Fridge Selection:** Choose which fridge to monitor
- **Time Range:** Select data time period
- **Auto Refresh:** Click Once to Start, Triple Click to Stop

### Status Colors
- 🟢 **Green:** Operating normally (0-50°C)
- 🔵 **Blue:** Too cold (below 0°F)
- 🔴 **Red:** Too warm (above 50°F)
- ⚪ **Gray:** No data available

### Contact
For technical support, please contact:
[support@fridgemonitoring.org](mailto:rvacf)
"""

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = """
- **R** - Manually refresh data
- **F** - Toggle fullscreen
- **S** - Save current view
"""

# Data refresh rate in seconds
REFRESH_RATE = 5