import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("ilovejuicebar_com")


def addy_ext(addy):
    address = addy.split(",")
    city = address[0]
    state_zip = address[1].strip().split(" ")
    state = state_zip[0]
    try:
        zip_code = state_zip[1]
    except:
        zip_code = "<MISSING>"
    return city, state, zip_code


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.ilovejuicebar.com"
    ext = "/locations"

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    states = base.find_all(class_="sqs-layout sqs-grid-12 columns-12")
    link_list = []
    for state in states:
        ps = state.find_all("p")
        for p in ps:
            try:
                href = p.a["href"]
                if (
                    "/menu" not in href
                    and "/contact" not in href
                    and "locations" not in href
                    and "#page" not in href
                ):
                    main = list(p.stripped_strings)
                    link_list.append([locator_domain + href, main])
            except:
                pass

    for row in link_list:
        link = row[0]
        if "com/" not in link:
            link = link.replace("com", "com/")
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        logger.info(link)

        raw_address = row[1]
        if not raw_address[-1].strip():
            raw_address.pop(-1)
        if "Temporarily" in raw_address[-1]:
            location_type = raw_address[-1]
            raw_address.pop(-1)
        else:
            location_type = ""

        street_address = " ".join(raw_address[1:-1])
        city, state, zip_code = addy_ext(raw_address[-1])
        country_code = "US"
        location_name = raw_address[0].strip()

        if "Suite" in city:
            street_address = " ".join(city.split()[:-1])
            city = city.split()[-1]

        if "Hill 412" in street_address:
            location_name = location_name + " Hill"
            street_address = street_address.replace("Hill", "").strip()

        if location_name == "Plaza Midwood1204 Central Avenue":
            location_name = "Plaza Midwood"
            street_address = "1204 Central Avenue Suite 100"

        main = list(
            base.find(class_="sqsrte-large").find_previous("div").stripped_strings
        )

        hours = ""
        phone_number = ""
        for h in main:
            if "//" in h or "am-" in h or "am -" in h:
                hours += h + " "
            try:
                phone_number = re.findall(r".+[0-9]{3}-[0-9]{4}", h)[0]
            except:
                pass

        hours = hours.replace("–", "-").strip()

        data = base.find("div", {"class": re.compile(r"sqs-block map-block.+")})[
            "data-block-json"
        ]
        json_coord = json.loads(data)

        lat = json_coord["location"]["markerLat"]
        longit = json_coord["location"]["markerLng"]
        store_number = "<MISSING>"

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
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
