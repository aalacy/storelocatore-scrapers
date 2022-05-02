import json

from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):

    base_link = "https://stores.cosmoprofbeauty.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "cosmoprofbeauty.com"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []

    main_items = base.find(id="bowse-content").find_all(class_="ga-link")
    for main_item in main_items:
        main_link = main_item["href"]

        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        next_items = base.find(class_="map-list").find_all(class_="ga-link")
        for next_item in next_items:
            next_link = next_item["href"]
            next_req = session.get(next_link, headers=headers)
            next_base = BeautifulSoup(next_req.text, "lxml")

            other_links = next_base.find(class_="map-list").find_all(
                class_="map-list-links"
            )
            for other_link in other_links:
                link = other_link.a["href"]
                final_links.append(link)

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
        if " " in zip_code or not zip_code[0].isdigit():
            country_code = "CA"
        if "/pr/" in final_link:
            country_code = "PR"
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
