import aiohttp

async def get_address_nominatim(lat: float, lon: float) -> dict:
    
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1"
    headers = {"User-Agent": "MyTestApp/1.0"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return {"error": "Не удалось получить адрес"}

            data = await resp.json()

    address = data.get("address", {})
    return {
        "city": address.get("city") or address.get("town") or address.get("village"),
        "street": address.get("road"),
        "house": address.get("house_number"),
    }