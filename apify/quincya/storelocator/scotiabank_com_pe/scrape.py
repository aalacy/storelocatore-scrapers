import re

from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.PERU],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
    )
    for postcode in search:

        base_link = (
            "https://intl.scotiabank.com/es-pe/locator/Mapa.aspx?q="
            + postcode
            + "&t=branch"
        )

        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find(id="branchList").div.find_all(class_="beam")

        locator_domain = "https://www.scotiabank.com.pe/"

        for item in items:
            location_name = item.find(class_="mapLink").text
            try:
                raw_address = (
                    (
                        item.find_all(class_="pillar")[3]
                        .text.replace("\r\n", " ")
                        .strip()
                    )
                    .encode("latin1")
                    .decode("utf8")
                )
            except:
                raw_address = (
                    item.find_all(class_="pillar")[3].text.replace("\r\n", " ").strip()
                )
            raw_address = (re.sub(" +", " ", raw_address)).strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if len(street_address) < 10:
                street_address = raw_address
            city = addr.city
            state = addr.state
            zip_code = addr.postcode

            if not city and not state:
                street_address = (
                    item.find_all(class_="pillar")[3]
                    .text.strip()
                    .split("\r\n")[0]
                    .strip()
                )
                city = (
                    item.find_all(class_="pillar")[3]
                    .text.strip()
                    .split("\r\n")[1]
                    .strip()
                )
            country_code = "Peru"
            store_number = ""
            location_type = ""
            phone = ""
            hours_of_operation = " ".join(list(item.table.stripped_strings)[:-1])
            latitude = item["lat"]
            longitude = item["lng"]
            search.found_location_at(latitude, longitude)

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=base_link,
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
                    raw_address=raw_address,
                )
            )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
