import json

from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):

    base_link = "https://stores.cosmoprofbeauty.com/sitemap.xml"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "cosmoprofbeauty.com"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []
    locs = base.find_all("loc")
    for loc in locs:
        if "/salon-supply" in loc.text:
            final_links.append(loc.text)

    for final_link in final_links:
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find_all("script", attrs={"type": "application/ld+json"})[
            -1
        ].contents[0]
        store = json.loads(script)[0]

        location_name = base.find(class_="location-name").text.strip()
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["address"]["telephone"]
        hours_of_operation = " ".join(list(base.find(class_="hours").stripped_strings))
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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
