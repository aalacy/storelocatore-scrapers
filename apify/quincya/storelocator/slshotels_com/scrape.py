import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.sbe.com/hotels/sls-hotels"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="card__link btn btn--primary")
    locator_domain = "sbe.com"

    for item in items:
        link = "https://www.sbe.com" + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find(class_="region region-content").script.contents[0]
        store = json.loads(script)

        location_name = store["name"]
        if "coming soon" in location_name.lower():
            continue
        country_code = store["address"]["addressCountry"]
        if country_code not in ["US", "CA"]:
            continue
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["telephone"]
        hours_of_operation = "<MISSING>"

        if street_address == "805 South Miami Ave":
            latitude = "25.765855"
            longitude = "-80.193079"
        else:
            try:
                map_link = store["hasMap"]
                at_pos = map_link.rfind("@")
                latitude = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
                longitude = map_link[
                    map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
                ].strip()
            except:
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
