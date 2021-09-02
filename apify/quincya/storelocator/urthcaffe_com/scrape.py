import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.urthcaffe.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = []

    # Using phones to match lat/lng
    geos = re.findall(r'[0-9]{2}\.[0-9]+,"lng":-[0-9]{2,3}\.[0-9]+', str(base))
    phones = re.findall(r'"phone":"[0-9]+', str(base))
    names = re.findall(r'"name":"[a-z A-Z]+","openTableId', str(base))
    if len(geos) - len(names) == 1:
        geos.pop(0)
        phones.pop(0)

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "addressLocality" in str(script):
            items.append(script.contents[0])

    for item in items:
        store = json.loads(item)

        locator_domain = "urthcaffe.com"
        street_address = store["address"]["streetAddress"].replace("\n", " ")
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = store["telephone"]
        for i, tel in enumerate(phones):
            if phone == tel.split('"')[-1]:
                geo = geos[i]
                latitude = geo.split(",")[0]
                longitude = geo.split(":")[-1]
                location_name = names[i].split(':"')[1].split('",')[0]

        hours_of_operation = " ".join(store["openingHours"])
        link = store["url"]

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
