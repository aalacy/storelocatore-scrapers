import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("freshiesdeli_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://freshiesdeli.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    all_links = []

    req = session.get(base_link, headers=headers)
    base_str = str(BeautifulSoup(req.text, "lxml"))

    all_links = re.findall(
        r"https://www.freshiesdeli.com/storelocations/[a-z]+", base_str
    )
    geos = re.findall(r"LatLng\([0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\);", base_str)[1:]
    for i, link in enumerate(all_links):
        if link == "https://www.freshiesdeli.com/storelocations/machiasfreshies":
            link = "https://freshiesdeli.com/storelocations/machaisfreshies"
        logger.info(link)

        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        locator_domain = "freshiesdeli.com"

        location_name = item.find("meta", attrs={"property": "og:title"})[
            "content"
        ].replace("—", "-")
        phone = item.find("meta", attrs={"itemprop": "description"})["content"][
            -15:
        ].strip()
        if "(" not in phone:
            phone = item.find("meta", attrs={"itemprop": "description"})["content"][
                3:18
            ].strip()
            raw_address = (
                item.find("meta", attrs={"itemprop": "description"})["content"][20:]
                .replace("St ", "St. ")
                .replace("Trail ", "Trail. ")
                .replace("", "")
                .strip()
            )
        else:
            raw_address = (
                item.find("meta", attrs={"itemprop": "description"})["content"][3:-18]
                .replace("St ", "St. ")
                .replace("Trail ", "Trail. ")
                .replace("", "")
                .strip()
            )
        street_address = raw_address[: raw_address.find(".")]
        city = raw_address[raw_address.find(".") + 1 : raw_address.find(",")].strip()
        state = raw_address[-3:].strip()
        zip_code = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"

        location_type = ""
        raw_types = item.find(
            class_="summary-item-list-container sqs-gallery-container"
        ).find_all(class_="summary-item")
        for row in raw_types:
            location_type = location_type + ", " + row.img["alt"]
        location_type = location_type[1:].strip()

        if "24 Hours" in location_type:
            hours_of_operation = "Open 24 Hours"
        else:
            hours_of_operation = ""

        latitude = geos[i].split("(")[1].split(",")[0]
        longitude = geos[i].split(",")[1][:-2]

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
