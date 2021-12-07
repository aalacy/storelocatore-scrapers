import json
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    url = "https://www.medstarhealth.org//sxa/search/results/?s={3D6661A6-0F00-4C7C-A8E9-6E8F15B6528B}&itemid={EB24C2F5-4CC8-4C57-8505-D865C498C3ED}&sig=locationsearch&distance%20by%20miles=25000&p=1000&o=Navigation%20Title%2CAscending&v=%7B1844930B-B644-4B06-84D9-68B7F7EDE9A0%7D"

    session = SgRequests(verify_ssl=False)
    items = session.get(url, headers=headers).json()["Results"]

    locator_domain = "medstarhealth.org"

    for item in items:
        link = "https://www.medstarhealth.org" + item["Url"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = (
            base.find("script", attrs={"type": "application ld-json"})
            .contents[0]
            .replace("\r\n", "")
            .replace("\t", "")
            .replace(",},", "},")
            .replace('" "', '""')
            .replace('""Mo', '"Mo')
            .replace('0""', '0"')
        )
        store = json.loads(script)
        location_name = base.h1.text.strip()
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["addressCountry"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["telephone"]
        hours_of_operation = store["openingHours"]

        latitude = base.find(class_="field-distance").span["data-lat"]
        longitude = base.find(class_="field-distance").span["data-lon"]

        if " " in zip_code:
            state = zip_code.split()[0]
            zip_code = zip_code.split()[1].strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
