import json
import cloudscraper

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.sweetfin.com/locations"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'window.POPMENU_APOLLO_STATE =')]/text()")
    )
    text = (
        text.split("window.POPMENU_APOLLO_STATE =")[1]
        .split("window.POPMENU")[0]
        .strip()[:-1]
        .replace('" + "', "")
    )
    js = json.loads(text)

    for key, j in js.items():
        if "RestaurantLocation:" not in key:
            continue

        raw_address = j.get("fullAddress")
        street_address = j.get("streetAddress")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = j.get("country")
        store_number = j.get("id")
        location_name = j.get("name")
        slug = j.get("slug")
        page_url = f"{locator_domain}{slug}"
        phone = j.get("displayPhone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = ";".join(j.get("schemaHours") or [])

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.sweetfin.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    session = cloudscraper.create_scraper()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
