# Sri Lanka festival calendar

FESTIVALS = [
    {
        "name": "Sinhala and Tamil New Year",
        "category": "FESTIVAL",
        "month": 4,
        "day_range": (13, 14),
        "regions": ["Island-wide"],
        "description": "Traditional Sri Lankan New Year with rituals, games and special foods",
        "tip": "Book accommodation early — very busy period"
    },
    {
        "name": "Vesak Festival",
        "category": "FESTIVAL",
        "month": 5,
        "day_range": (1, 31),
        "regions": ["Island-wide"],
        "description": "Buddhist festival with lanterns and pandols across Sri Lanka",
        "tip": "Visit Colombo for the most spectacular pandols"
    },
    {
        "name": "Esala Perahera",
        "category": "FESTIVAL",
        "month": 8,
        "day_range": (1, 15),
        "regions": ["Kandy"],
        "description": "Grand procession with elephants, drummers and fire dancers",
        "tip": "Book tickets and accommodation 3+ months in advance"
    },
    {
        "name": "Elephant Gathering — Minneriya",
        "category": "WILDLIFE",
        "month": 8,
        "day_range": (1, 31),
        "regions": ["Minneriya", "Sigiriya"],
        "description": "Hundreds of wild elephants gather at Minneriya Tank",
        "tip": "Evening safaris (4-6pm) offer the best viewing"
    },
    {
        "name": "Kataragama Festival",
        "category": "RELIGIOUS",
        "month": 7,
        "day_range": (28, 31),
        "regions": ["Kataragama", "Yala"],
        "description": "Major religious festival attended by all communities",
        "tip": "Firewalking ceremony is the highlight"
    },
    {
        "name": "Diwali",
        "category": "RELIGIOUS",
        "month": 10,
        "day_range": (1, 31),
        "regions": ["Island-wide"],
        "description": "Festival of lights celebrated by Tamil community",
        "tip": "Jaffna has the most vibrant celebrations"
    },
    {
        "name": "Christmas in Galle Fort",
        "category": "FESTIVAL",
        "month": 12,
        "day_range": (24, 26),
        "regions": ["Galle"],
        "description": "Unique Christmas celebrations inside historic Galle Fort",
        "tip": "Magical atmosphere inside the fort walls"
    },
    {
        "name": "Arugam Bay Surf Season",
        "category": "SURF",
        "month_range": (5, 10),
        "regions": ["Arugam Bay"],
        "description": "World-class surf season at Arugam Bay",
        "tip": "June-August has the most consistent waves"
    },
    {
        "name": "Whale Watching Season",
        "category": "WILDLIFE",
        "month_range": (11, 4),
        "regions": ["Mirissa", "Trincomalee"],
        "description": "Blue whale and sperm whale sightings off south coast",
        "tip": "November to April from Mirissa, May to October from Trincomalee"
    },
]

def get_festivals_for_dates(start_month: int, end_month: int,
                            regions: list) -> list:
    matching = []
    months = list(range(start_month, end_month + 1))

    for festival in FESTIVALS:
        festival_months = []

        if "month" in festival:
            festival_months = [festival["month"]]
        elif "month_range" in festival:
            s, e = festival["month_range"]
            festival_months = list(range(s, e + 1)) \
                if s <= e else list(range(s, 13)) + list(range(1, e + 1))

        # Month match
        month_match = any(m in months for m in festival_months)

        # Region match
        region_match = any(
            fr.lower() in ["island-wide"] or
            any(r.lower() in fr.lower() or fr.lower() in r.lower()
                for r in regions)
            for fr in festival.get("regions", [])
        )

        if month_match and region_match:
            matching.append(festival)

    return matching