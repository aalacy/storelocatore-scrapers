from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    locator_domain = "https://www.take5oilchange.com"

    url = "https://www.take5oilchange.com/api/stores"
    res_json = session.get(url, headers=HEADERS).json()

    for loc in res_json:
        if loc["IsUpcomingStore"]:
            continue

        street_address = loc["Location_Address"]
        city = loc["Location_City"]
        state = loc["Location_State"]

        zip_code = loc["Location_PostalCode"]
        store_number = loc["License_Number"]

        longit = loc["Location_Longitude"]
        lat = loc["Location_Latitude"]
        phone_number = loc["PhoneNumber_Display"].strip()
        location_name = loc["Center_Name"]
        country_code = "US"
        location_type = "<MISSING>"

        hours = "Monday " + loc["Monday_Open"] + " - " + loc["Monday_Close"] + " "
        hours += "Tuesday " + loc["Tuesday_Open"] + " - " + loc["Tuesday_Close"] + " "
        hours += (
            "Wednesday " + loc["Wednesday_Open"] + " - " + loc["Wednesday_Close"] + " "
        )
        hours += (
            "Thursday " + loc["Thursday_Open"] + " - " + loc["Thursday_Close"] + " "
        )
        hours += "Friday " + loc["Friday_Open"] + " - " + loc["Friday_Close"] + " "
        hours += (
            "Saturday " + loc["Saturday_Open"] + " - " + loc["Saturday_Close"] + " "
        )

        if "Closed" in loc["Sunday_Open"]:
            hours += "Sunday Closed"
        else:
            hours += "Sunday " + loc["Sunday_Open"] + " - " + loc["Sunday_Close"] + " "
        hours = hours.strip()

        page_url = loc["Center_Website"]
        if not page_url:
            page_url = "https://www.take5oilchange.com/locations/"
            if "5205 Rufe Snow" in street_address:
                page_url = "https://www.take5oilchange.com/locations/tx/north-richland-hills-670/"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
