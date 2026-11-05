SCENARIOS = {
    "NORMAL": {
        "panel": {
            "voltage": (12.0, 15.0),
            "current": (500.0, 1500.0)
        },
        "beban": {
            "voltage": (4.5, 6.0),
            "current": (100.0, 500.0)
        },
        "baterai": {
            "voltage": (12.0, 14.5),
            "current": (-1200.0, -300.0)   # negatif = discharge (keluar dari baterai)
        }
    },

    "LOW_BATTERY": {
        "panel": {
            "voltage": (12.0, 15.0),
            "current": (500.0, 1500.0)
        },
        "beban": {
            "voltage": (4.5, 6.0),
            "current": (100.0, 500.0)
        },
        "baterai": {
            "voltage": (10.5, 11.9),       # di bawah ambang warning (12.0V)
            "current": (-800.0, -200.0)
        }
    },

    "HIGH_LOAD": {
        "panel": {
            "voltage": (12.0, 15.0),
            "current": (500.0, 1500.0)
        },
        "beban": {
            "voltage": (4.5, 6.0),
            "current": (500.0, 1000.0)
        },
        "baterai": {
            "voltage": (12.0, 14.5),
            "current": (-3500.0, -1500.0)  # discharge tinggi, lewati ambang critical (-3000)
        }
    },

    "LOW_PANEL_OUTPUT": {
        "panel": {
            "voltage": (12.0, 14.0),
            "current": (100.0, 400.0)
        },
        "beban": {
            "voltage": (4.5, 6.0),
            "current": (100.0, 500.0)
        },
        "baterai": {
            "voltage": (12.0, 14.5),
            "current": (-1200.0, -300.0)
        }
    }
}

def get_scenario(name):
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}")

    return SCENARIOS[name]
