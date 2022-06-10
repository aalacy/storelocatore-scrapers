from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    session = SgRequests()

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.snapfitness.com",
        "Origin": "https://www.snapfitness.com",
        "Referer": "https://www.snapfitness.com/us/gyms/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    locator_domain = "snapfitness.com"

    base_link = "https://www.snapfitness.com/us/gyms/relevantLocations"

    payload = {
        "lat": "44.977753",
        "limitToCountry": "false",
        "long": "-93.265015",
        "radius": "20236.899793572078",
        "search": "",
    }

    res_json = session.post(base_link, headers=headers, data=payload).json()

    for i in res_json:
        loc = res_json[i]
        try:
            location_name = (
                "Snap Fitness " + loc["Name"].replace("Cronulla", "").strip()
            )
        except:
            continue

        phone_number = loc["PhoneNumber"]
        if not phone_number:
            phone_number = "<MISSING>"
        lat = loc["Latitude"]
        longit = loc["Longitude"]
        try:
            street_address = (loc["Address1"] + " " + loc["Address2"]).strip()
        except:
            street_address = loc["Address1"]
        try:
            city = loc["City"].replace("Cronulla", "")
        except:
            city = loc["City"]
        state = loc["State"]
        zip_code = loc["Postcode"]
        country_code = loc["Country"]
        store_number = loc["ID"]

        hours = "<INACCESSIBLE>"
        page_url = (
            "https://www.snapfitness.com"
            + loc["URL"].replace("stage=Stage", "").strip()
        )
        page_url = page_url.replace("?", "")
        if "cronulla" in page_url:
            page_url = "<INACCESSIBLE>"
        location_type = "<MISSING>"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
