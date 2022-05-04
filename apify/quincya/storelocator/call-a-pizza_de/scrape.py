import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.call-a-pizza.de/bestellen"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.call-a-pizza.de"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="bestellen_store")
    for item in items:

        link = locator_domain + item.a["href"]
        location_name = item.strong.text
        street_address = (
            item.find(attrs={"itemprop": "streetAddress"}).text.split("(")[0].strip()
        )
        city = item["data-city"]
        state = item["data-state"]
        zip_code = item.find(attrs={"itemprop": "postalCode"}).text.strip()
        country_code = "Germany"
        phone = item.find(attrs={"itemprop": "telephone"}).text.strip()

        store_number = item["data-id"]
        location_type = "<MISSING>"

        raw_hours = list(item.find(class_="bestellen_oph valign_top").stripped_strings)[
            1:
        ]

        hours_of_operation = ""
        for num, row in enumerate(raw_hours):
            if "(" in row:
                hours_of_operation = " ".join(raw_hours[:num])
                break
        if not hours_of_operation:
            hours_of_operation = " ".join(raw_hours)

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = script = base.find_all(
            "script", attrs={"type": "application/ld+json"}
        )[-1].contents[0]
        store = json.loads(script)

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

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
