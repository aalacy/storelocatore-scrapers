import math

from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    country = line.split(",")[-1].strip()
    post = line.split(",")[-2].strip()
    adr = parse_address(International_Parser(), line, country=country, postcode=post)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING
    country = adr.country or SgRecord.MISSING

    return street, city, postal, country


def get_bounds(latitude, longitude, distance):
    radius = 6371

    lat = math.radians(latitude)
    lng = math.radians(longitude)
    parallel_radius = radius * math.cos(lat)

    lat_min = lat - distance / radius
    lat_max = lat + distance / radius
    lon_min = lng - distance / parallel_radius
    lon_max = lng + distance / parallel_radius
    rad2deg = math.degrees

    bottom = rad2deg(lat_min)
    left = rad2deg(lon_min)
    top = rad2deg(lat_max)
    right = rad2deg(lon_max)

    return top, bottom, right, left


def fetch_data(sgw: SgWriter):
    countries = ["be", "cz", "de", "fr", "gb", "it", "nl", "pt"]
    search = DynamicGeoSearch(country_codes=countries, expected_search_radius_miles=10)
    for lat, lng in search:
        to, bo, ri, le = get_bounds(lat, lng, 150)
        data = {
            "longitude": str(lng),
            "latitude": str(lat),
            "take": "50",
            "zoomLevel": "8",
            "availableOnly": "false",
            "fromCache": "false",
            "Top": str(to),
            "Left": str(bo),
            "Bottom": str(ri),
            "Right": str(le),
        }

        r = session.post(api, headers=headers, data=data, cookies=cookies)
        js = r.json()
        if not js:
            search.found_nothing()

        for j in js:
            if j.get("MarkerType") != "Location":
                continue

            location_name = j.get("Name")
            raw_address = j.get("HtmlAddress") or ""
            if "*" in raw_address:
                raw_address = (
                    raw_address.split("*")[0].strip()
                    + " "
                    + raw_address.split("*")[-1].strip()
                )
            if "(" in raw_address:
                raw_address = (
                    raw_address.split("(")[0].strip()
                    + " "
                    + raw_address.split(")")[-1].strip()
                )
            street_address, city, postal, country_code = get_international(raw_address)
            store_number = j.get("Uid")
            phone = j.get("Phone") or ""
            if "Gated" in phone:
                phone = SgRecord.MISSING
            hours_of_operation = j.get("OperationHours")
            latitude = j.get("Lat")
            longitude = j.get("Long")
            search.found_location_at(latitude, longitude)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                raw_address=raw_address,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.hertz247.co.uk/"
    api = "https://www.hertz247.co.uk/Reservation/GetLocations"
    page_url = "https://www.hertz247.co.uk/uk/en-gb/location/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.hertz247.co.uk/uk/en-gb/reservation",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.hertz247.co.uk",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    with SgRequests() as session:
        cookies = {"service_preference": "wL7n1KFxrW7FrAt5z5WEbA=="}
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
            )
        ) as writer:
            fetch_data(writer)
