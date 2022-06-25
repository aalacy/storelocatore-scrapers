import re

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://heroburgers.com/"
    location_url = "https://onlineordering.zone1.mealsyservices.com/api/v1/Companies/POSHeroCertifiedBurgers/Businesses"
    r = session.get(location_url, headers=headers)
    json_data = r.json()

    for val in json_data["Businesses"]:
        location_name = val["Foodprovider"]["Name"]
        addr = val["Foodprovider"]["Address"].split(",")
        if len(addr) == 4:
            street_address = ",".join(addr[:2]).strip()
            city = addr[2].strip()
            state = addr[-1].strip()
            country_code = "CA"
        elif len(addr) == 3:
            street_address = addr[0].strip()
            city = addr[1].strip()
            state = addr[2].strip()
            country_code = "CA"
        else:
            city = "New York"
            street_address = addr[0].replace(city, "").strip()
            state = addr[1].strip()
            country_code = "US"

        if re.search(r"\d", street_address):
            digit = str(re.search(r"\d", street_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = street_address[start:]

        zipp = val["Foodprovider"]["PostalCode"]
        store_number = val["Foodprovider"]["Id"]
        phone = val["Foodprovider"]["Tell"]
        latitude = val["Foodprovider"]["Latitude"]
        longitude = val["Foodprovider"]["Longitude"]

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url="https://onlineordering.heroburgers.com/en/#/HeroCertifiedBurgers/online/restaurant-selection",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
