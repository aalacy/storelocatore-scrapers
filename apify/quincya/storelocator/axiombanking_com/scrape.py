from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://www.axiombanking.com/locations"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    code = str(base).split('buildId":"')[1].split('"')[0]

    api_link = (
        "https://www.axiombanking.com/_next/data/" + code + "/en-US/locations.json"
    )
    stores = session.get(api_link, headers=headers).json()["pageProps"]["locations"]

    locator_domain = "axiombanking.com"

    for store in stores:
        raw_hours = store["locationFields"]["lobbyHours"]["customHours"]
        hours_of_operation = ""
        if raw_hours:
            for hours in raw_hours:
                day = hours["day"]
                if hours["isClosed"]:
                    clean_hours = day + " Closed"
                else:
                    opens = hours["opens"]
                    closes = hours["closes"]
                    clean_hours = day + " " + opens + "-" + closes
                    hours_of_operation = (
                        hours_of_operation + " " + clean_hours
                    ).strip()
            standard_hours = hours_of_operation

    for store in stores:
        location_name = store["title"]
        raw_address = store["locationFields"]["address"]["streetAddress"].split(",")
        street_address = " ".join(raw_address[:-3])
        city = raw_address[-3].strip()
        state_line = raw_address[-2].strip()
        state = state_line.split()[0]
        try:
            zip_code = state_line.split()[1]
        except:
            zip_code = ""
        country_code = raw_address[-1].strip()
        store_number = "<MISSING>"
        phone = store["locationFields"]["contactInformation"]["phoneNumber"]
        latitude = store["locationFields"]["address"]["latitude"]
        longitude = store["locationFields"]["address"]["longitude"]
        raw_types = store["locationFields"]["locationType"]
        location_type = raw_types[0]["name"]
        if len(raw_types) > 1:
            for row in raw_types[1:]:
                location_type = (location_type + ", " + row["name"]).strip()
        raw_hours = store["locationFields"]["lobbyHours"]["customHours"]
        hours_of_operation = ""
        if raw_hours:
            for hours in raw_hours:
                day = hours["day"]
                if hours["isClosed"]:
                    clean_hours = day + " Closed"
                else:
                    opens = hours["opens"]
                    closes = hours["closes"]
                    clean_hours = day + " " + opens + "-" + closes
                    hours_of_operation = (
                        hours_of_operation + " " + clean_hours
                    ).strip()
        else:
            hours_of_operation = standard_hours

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url="https://www.axiombanking.com/locations",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
