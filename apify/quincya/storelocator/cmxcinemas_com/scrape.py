import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "cmxcinemas.com"

    base_link = "https://www.cmxcinemas.com/location"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    states = list(base.find(id="drpStateloc").stripped_strings)[1:]
    api_link = "https://www.cmxcinemas.com/Locations/FilterLocations?state="

    for st in states:
        stores = session.get(api_link + st, headers=headers).json()["listloc"][0][
            "city"
        ]

        for store in stores:

            link = "https://www.cmxcinemas.com/Locationdetail/" + store["slugname"]

            location_name = store["cinemaname"]
            street_address = store["address"].split(", MN")[0].strip()
            city = store["locCity"].replace("MN", "").strip()
            state = st
            zip_code = store["postalcode"].replace("21075", "20175")
            country_code = "US"

            store_number = "<MISSING>"
            hours_of_operation = "<MISSING>"
            location_type = "<MISSING>"

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                map_link = base.find(class_="map-blk").iframe["src"]
            except:
                continue

            try:
                phone = (
                    re.findall(
                        r"Contact Us:.+[0-9]{4}", str(base.find(class_="aboutus-cont"))
                    )[0]
                    .split(":")[1]
                    .strip()
                )
            except:
                phone = "<MISSING>"
            try:
                lat_pos = map_link.rfind("!3d")
                latitude = map_link[
                    lat_pos + 3 : map_link.find("!", lat_pos + 5)
                ].strip()
                lng_pos = map_link.find("!2d")
                longitude = map_link[
                    lng_pos + 3 : map_link.find("!", lng_pos + 5)
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
