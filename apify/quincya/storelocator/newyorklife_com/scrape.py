import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("newyorklife_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.newyorklife.com/careers/go-directory"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=HEADERS)
    base = BeautifulSoup(req.text, "lxml")

    found_poi = []

    items = base.find_all("a", {"href": re.compile(r"careers/become-an-agent/")})
    locator_domain = "newyorklife.com"

    for item in items:
        link = "https://www.newyorklife.com" + item["href"]
        if link in found_poi:
            continue
        found_poi.append(link)
        logger.info(link)
        req = session.get(link, headers=HEADERS)
        if req.status_code == 404:
            continue
        base = BeautifulSoup(req.text, "lxml")

        script = base.find_all("script", attrs={"type": "application/ld+json"})[
            -1
        ].text.strip()
        store = json.loads(script)

        location_name = "New York Life"
        street_address = store["address"]["streetAddress"].strip()

        digit = str(re.search(r"\d", street_address))
        start = int(digit.split("(")[1].split(",")[0])
        if (
            start != 0
            and "THREE CITY PLACE" not in street_address.upper()
            and "BISHOP RANCH #3" not in street_address.upper()
            and "SOUTH TOWNE CORPORATE" not in street_address.upper()
        ):
            location_name = street_address[:start].strip()
            street_address = street_address[start:]
        if "THREE CITY PLACE" in street_address:
            location_name = location_name + " - CITY PLACE THREE"
            street_address = "THREE CITY PLACE DRIVE SUITE 690"
        if "BISHOP RANCH #3" in street_address:
            location_name = location_name + " - BISHOP RANCH #3"
            street_address = "2633 CAMINO RAMON SUITE 525"
        if "SOUTH TOWNE CORPORATE" in street_address:
            location_name = location_name + " - SOUTH TOWNE CORPORATE CENTER 1"
            street_address = "150 WEST CIVIC CENTER DRIVE SUITE 600"

        city = store["address"]["addressLocality"].strip()
        state = store["address"]["addressRegion"].strip()
        zip_code = store["address"]["postalCode"].strip()
        country_code = store["address"]["addressCountry"].strip()
        store_number = "<MISSING>"
        phone = store["telephone"]
        location_type = "<MISSING>"
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]
        hours_of_operation = "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name.upper(),
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

        # Other locations

        locs = base.find(class_="cmp-locations").ul.find_all("li")
        if len(locs) > 1:
            other_locs = locs[1:]
            for loc in other_locs:
                location_name = "New York Life"
                loc_list = (
                    loc.text[: loc.text.rfind("Office")]
                    .replace("\r", "")
                    .replace("Fax:", "")
                    .replace(" \n ", "")
                    .replace("|", "")
                    .strip()
                    .split("\n")
                )
                street_address = " ".join(loc_list[:-1])
                street_address = (re.sub(" +", " ", street_address)).strip()
                if street_address[-1:] == ",":
                    street_address = street_address[:-1]
                if street_address[:1] == ",":
                    street_address = street_address[1:].strip()

                digit = str(re.search(r"\d", street_address))
                start = int(digit.split("(")[1].split(",")[0])
                if start != 0:
                    location_name = street_address[:start].strip()
                    street_address = street_address[start:]
                    if location_name[-1:] == ",":
                        location_name = location_name[:-1].strip()

                city_line = loc_list[-1].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                try:
                    zip_code = city_line[-1].strip().split()[1].strip()
                except:
                    zip_code = "<MISSING>"
                country_code = "US"
                store_number = "<MISSING>"

                try:
                    phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(loc.text))[0]
                except:
                    phone = "<MISSING>"

                location_type = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=link,
                        location_name=location_name.upper(),
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


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
