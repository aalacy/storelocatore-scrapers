import re
import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.localiyours.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("script", attrs={"type": "application/ld+json"})

    js = base.find(id="popmenu-apollo-state").contents[0]
    lats = re.findall(r'lat":[0-9]{2}\.[0-9]+', str(js))
    lngs = re.findall(r'lng":-[0-9]{2,3}\.[0-9]+', str(js))

    if len(lats) > len(items):
        lats.pop(0)
        lngs.pop(0)

    for i, item in enumerate(items):
        store = json.loads(item.contents[0])

        locator_domain = "localiyours.com"

        street_address = (
            store["address"]["streetAddress"]
            .replace("\n", " ")
            .split("The Academy")[0]
            .strip()
        )
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["telephone"]

        hours_of_operation = " ".join(store["openingHours"])

        link = store["hasMenu"]
        location_name = link.split("/")[-1].replace("-", " ").title()

        latitude = lats[i].split(":")[1]
        longitude = lngs[i].split(":")[1]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
