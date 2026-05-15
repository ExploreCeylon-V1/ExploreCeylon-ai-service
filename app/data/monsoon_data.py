# Sri Lanka monsoon data by region and month

# SW Monsoon: May-September → affects West, South, Hill Country
# NE Monsoon: October-January → affects North, East

MONSOON_DATA = {
    "SW_MONSOON": {
        "months": [5, 6, 7, 8, 9],
        "affected_regions": [
            "Colombo", "Galle", "Mirissa",
            "Nuwara Eliya", "Kandy",
            "West Coast", "South Coast", "Hill Country"
        ],
        "safe_regions": [
            "Arugam Bay", "Trincomalee",
            "Jaffna", "Batticaloa",
            "East Coast"
        ],
        "description": "Southwest monsoon brings heavy rainfall to "
                      "western and southern Sri Lanka. "
                      "East coast is ideal during this period."
    },
    "NE_MONSOON": {
        "months": [10, 11, 12, 1],
        "affected_regions": [
            "Trincomalee", "Jaffna",
            "Arugam Bay", "Batticaloa",
            "North Coast", "East Coast"
        ],
        "safe_regions": [
            "Galle", "Mirissa", "Colombo",
            "Yala", "Nuwara Eliya",
            "West Coast", "South Coast"
        ],
        "description": "Northeast monsoon affects northern and eastern "
                      "Sri Lanka. West and south coast are ideal."
    }
}

def get_monsoon_warning(regions: list, months: list) -> dict:
    warnings = []

    for month in months:
        # Check SW monsoon
        if month in MONSOON_DATA["SW_MONSOON"]["months"]:
            affected = [
                r for r in regions
                if any(
                    a.lower() in r.lower() or r.lower() in a.lower()
                    for a in MONSOON_DATA["SW_MONSOON"]["affected_regions"]
                )
            ]
            if affected:
                warnings.append({
                    "type": "SW_MONSOON",
                    "month": month,
                    "affected_regions": affected,
                    "description": MONSOON_DATA["SW_MONSOON"]["description"],
                    "recommendation": "Consider visiting east coast instead: "
                                     "Arugam Bay, Trincomalee"
                })

        # Check NE monsoon
        if month in MONSOON_DATA["NE_MONSOON"]["months"]:
            affected = [
                r for r in regions
                if any(
                    a.lower() in r.lower() or r.lower() in a.lower()
                    for a in MONSOON_DATA["NE_MONSOON"]["affected_regions"]
                )
            ]
            if affected:
                warnings.append({
                    "type": "NE_MONSOON",
                    "month": month,
                    "affected_regions": affected,
                    "description": MONSOON_DATA["NE_MONSOON"]["description"],
                    "recommendation": "Consider visiting west/south coast: "
                                     "Galle, Mirissa, Yala"
                })

    return {"warnings": warnings, "has_warning": len(warnings) > 0}