import re
import json
import time
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgselenium import SgFirefox
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser

page_url = "https://www.vodafone.com.tr/YardimDestek/vodafone-magazalari"


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_locations(session, retry=0):
    try:
        session.get(page_url)
        session.find_element_by_id("onetrust-accept-btn-handler").click()
        time.sleep(10)
        tree = BeautifulSoup(session.page_source, "html.parser")
        text = get_data_script(tree)
        return json.loads(text)
    except:
        if retry < 3:
            return get_locations(session, retry + 1)


def get_data_script(soup):
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and "dataCities" in script.string:
            data = re.search(r"var markers = \[(.*)\];", script.string).group(1)
            return f"[{data}]"


def fetch_data(sgw: SgWriter):
    with SgFirefox(is_headless=True).driver() as session:
        locations = get_locations(session)

        for j in locations:
            location_name = j.get("name")
            store_number = j.get("code")
            latitude = j.get("latitude") or ""
            if latitude.endswith(","):
                latitude = latitude[:-1]

            longitude = j.get("longitude")
            phone = j.get("phone")
            raw_address = j.get("address") or ""
            street_address, city, state, postal = get_international(
                re.sub(r"\s\n", ", ", raw_address)
            )

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="TR",
                phone=phone,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.com.tr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
