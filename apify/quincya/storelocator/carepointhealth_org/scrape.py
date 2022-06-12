from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://carepointhealth.org/locations-directions/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    response = session.get(base_link, headers=headers)
    base = BeautifulSoup(response.text, "lxml")

    items = base.find(class_="elementor-section-wrap").find_all(
        class_="elementor-column"
    )
    locator_domain = "carepointhealth.org"

    for item in items:
        if "get directions" not in item.text.lower():
            continue
        raw_data = list(item.stripped_strings)[:-1]
        location_name = "CarePoint Health Medical Group"
        phone = "<MISSING>"
        link = base_link
        if len(raw_data) > 3:
            location_name = raw_data[0]
            phone = raw_data[-1].replace("Phone:", "").strip()
            link = "https://carepointhealth.org" + item.a["href"]
            raw_data.pop(0)
        street_address = raw_data[0].strip()
        city_line = raw_data[1]
        if "NJ" in city_line and "," not in city_line:
            city_line = city_line.replace(" NJ", ", NJ")
        city_line = city_line.split(",")
        if len(city_line) == 3:
            street_address = street_address + " " + city_line[0]
            city_line.pop(0)
        city = city_line[0].strip()
        state = city_line[1][:-6].strip()
        zip_code = city_line[-1][-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
