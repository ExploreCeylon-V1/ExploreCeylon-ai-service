import httpx
from typing import List, Optional

SPRING_BOOT_URL = "http://localhost:8080"

async def get_destinations(category: Optional[str] = None,
                           province: Optional[str] = None) -> list:
    try:
        params = {}
        if category: params["category"] = category
        if province: params["province"] = province

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/destinations",
                params=params
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (destinations): {e}")
        return []


async def get_featured_destinations() -> list:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/destinations/featured"
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (featured): {e}")
        return []


async def get_hidden_gems(category: Optional[str] = None,
                          district: Optional[str] = None) -> list:
    try:
        params = {}
        if category: params["category"] = category
        if district: params["district"] = district

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/gems",
                params=params
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (gems): {e}")
        return []


async def get_events(month: Optional[int] = None,
                     region: Optional[str] = None) -> list:
    try:
        params = {}
        if month:  params["month"]  = month
        if region: params["region"] = region

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/events",
                params=params
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (events): {e}")
        return []


async def search_destinations(keyword: str) -> list:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/destinations/search",
                params={"keyword": keyword}
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (destinations search): {e}")
        return []


async def get_nearby_destinations(lat: float, lng: float,
                                  limit: int = 15) -> list:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/destinations/nearby",
                params={"lat": lat, "lng": lng, "limit": limit}
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (destinations nearby): {e}")
        return []


async def get_nearby_gems(lat: float, lng: float,
                          limit: int = 10) -> list:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/gems/nearby",
                params={"lat": lat, "lng": lng, "limit": limit}
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (gems nearby): {e}")
        return []


async def get_events_trip_sync(start_date, end_date) -> list:
    try:
        params = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/events/trip-sync",
                params=params
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (events trip-sync): {e}")
        return []


async def get_guides(district: Optional[str] = None,
                     specialty: Optional[str] = None) -> list:
    try:
        params = {}
        if district:  params["district"]  = district
        if specialty: params["specialty"] = specialty

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(
                f"{SPRING_BOOT_URL}/api/v1/guides",
                params=params
            )
            if res.status_code == 200:
                return res.json()
            return []
    except Exception as e:
        print(f"DB service error (guides): {e}")
        return []