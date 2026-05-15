# Sri Lanka regions, districts and travel info

REGIONS = {
    "Colombo": {
        "district": "Colombo",
        "coordinates": {"lat": 6.9271, "lng": 79.8612},
        "highlights": [
            "Galle Face Green", "Pettah Market",
            "National Museum", "Gangaramaya Temple",
            "Viharamahadevi Park"
        ],
        "travel_time_from": {
            "Kandy": "3 hours by road, 2.5 hours by train",
            "Galle": "2 hours by road",
            "Ella": "6 hours by road",
        }
    },
    "Kandy": {
        "district": "Kandy",
        "coordinates": {"lat": 7.2906, "lng": 80.6337},
        "highlights": [
            "Temple of Tooth Relic", "Peradeniya Botanical Gardens",
            "Kandy Lake", "Royal Palace",
            "Udawatta Kele Forest"
        ],
        "travel_time_from": {
            "Colombo": "3 hours by road, 2.5 hours by train",
            "Ella": "3 hours by road",
            "Sigiriya": "2 hours by road"
        }
    },
    "Ella": {
        "district": "Badulla",
        "coordinates": {"lat": 6.8667, "lng": 81.0466},
        "highlights": [
            "Ella Rock", "Nine Arch Bridge",
            "Little Adams Peak", "Ravana Falls",
            "Tea plantations"
        ],
        "travel_time_from": {
            "Kandy": "3 hours by train (scenic)",
            "Colombo": "6 hours by road",
            "Yala": "3 hours by road"
        }
    },
    "Galle": {
        "district": "Galle",
        "coordinates": {"lat": 6.0535, "lng": 80.2210},
        "highlights": [
            "Galle Fort", "Jungle Beach",
            "Unawatuna Beach", "Mirissa nearby",
            "Koggala Lake"
        ],
        "travel_time_from": {
            "Colombo": "2 hours by road",
            "Mirissa": "30 minutes by road"
        }
    },
    "Sigiriya": {
        "district": "Matale",
        "coordinates": {"lat": 7.9570, "lng": 80.7603},
        "highlights": [
            "Sigiriya Rock Fortress", "Pidurangala Rock",
            "Dambulla Cave Temple", "Minneriya National Park"
        ],
        "travel_time_from": {
            "Colombo": "4 hours by road",
            "Kandy": "2 hours by road",
            "Anuradhapura": "1.5 hours by road"
        }
    },
    "Yala": {
        "district": "Hambantota",
        "coordinates": {"lat": 6.3728, "lng": 81.5216},
        "highlights": [
            "Yala National Park Safari",
            "Leopard spotting",
            "Elephant herds",
            "Crocodiles and birds"
        ],
        "travel_time_from": {
            "Galle": "3 hours by road",
            "Ella": "3 hours by road",
            "Colombo": "5 hours by road"
        }
    },
    "Nuwara Eliya": {
        "district": "Nuwara Eliya",
        "coordinates": {"lat": 6.9497, "lng": 80.7891},
        "highlights": [
            "Tea estates", "Horton Plains",
            "Worlds End", "Gregory Lake",
            "Victoria Park"
        ],
        "travel_time_from": {
            "Kandy": "2.5 hours by road",
            "Ella": "2 hours by road"
        }
    },
    "Mirissa": {
        "district": "Matara",
        "coordinates": {"lat": 5.9483, "lng": 80.4716},
        "highlights": [
            "Whale watching", "Mirissa Beach",
            "Coconut Hill", "Parrot Rock"
        ],
        "travel_time_from": {
            "Galle": "30 minutes by road",
            "Colombo": "3 hours by road"
        }
    },
    "Arugam Bay": {
        "district": "Ampara",
        "coordinates": {"lat": 6.8403, "lng": 81.8362},
        "highlights": [
            "Surfing", "Main Point surf break",
            "Whiskey Point", "Crocodile Rock",
            "Elephant safari nearby"
        ],
        "travel_time_from": {
            "Ella": "3 hours by road",
            "Colombo": "8 hours by road"
        }
    },
    "Trincomalee": {
        "district": "Trincomalee",
        "coordinates": {"lat": 8.5874, "lng": 81.2152},
        "highlights": [
            "Nilaveli Beach", "Pigeon Island",
            "Koneswaram Temple", "Fort Frederick",
            "Whale and dolphin watching"
        ],
        "travel_time_from": {
            "Colombo": "6 hours by road",
            "Sigiriya": "3 hours by road"
        }
    },
    "Jaffna": {
        "district": "Jaffna",
        "coordinates": {"lat": 9.6615, "lng": 80.0255},
        "highlights": [
            "Jaffna Fort", "Nainativu Island",
            "Nagadeepa Temple", "Jaffna Market",
            "Casuarina Beach"
        ],
        "travel_time_from": {
            "Colombo": "8 hours by road or 1 hour by plane",
            "Anuradhapura": "3 hours by road"
        }
    },
    "Anuradhapura": {
        "district": "Anuradhapura",
        "coordinates": {"lat": 8.3114, "lng": 80.4037},
        "highlights": [
            "Sacred Bodhi Tree", "Ruwanwelisaya Stupa",
            "Isurumuniya Temple", "Abhayagiri Monastery",
            "Wilpattu National Park nearby"
        ],
        "travel_time_from": {
            "Colombo": "4 hours by road",
            "Sigiriya": "1.5 hours by road"
        }
    },
}

# Regions that are TOO FAR to visit consecutively
INCOMPATIBLE_CONSECUTIVE = [
    ("Jaffna", "Yala"),
    ("Jaffna", "Arugam Bay"),
    ("Jaffna", "Mirissa"),
    ("Trincomalee", "Mirissa"),
    ("Trincomalee", "Yala"),
]

def get_region_names():
    return list(REGIONS.keys())

def get_highlights(region: str):
    return REGIONS.get(region, {}).get("highlights", [])

def check_incompatible(region1: str, region2: str) -> bool:
    pair = (region1, region2)
    reverse = (region2, region1)
    return pair in INCOMPATIBLE_CONSECUTIVE or \
           reverse in INCOMPATIBLE_CONSECUTIVE