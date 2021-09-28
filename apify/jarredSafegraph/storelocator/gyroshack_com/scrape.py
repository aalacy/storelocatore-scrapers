from typing import Any

import bs4
import re as regEx
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

domain = "https://www.gyroshack.com/"
logger = sglog.SgLogSetup().get_logger(logger_name=domain)


def fetch_raw_using():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    locations_page = SgRequests().request(
        f"{domain}wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php",
        headers=headers,
    )
    stores = []
    if locations_page.status_code == 200:
        logger.debug(f"Nothing fishy here: {locations_page}")
        try:
            stores = xml_to_dict(locations_page)
        except Exception as err:
            logger.error(
                f"error by status_code: {locations_page.status_code} for {domain}wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
            )
            logger.debug(str(err))
    else:
        logger.debug(f"Something fishy here: {locations_page}")

    yield stores


def xml_to_dict(locations_page):
    stores = []
    soup = bs4.BeautifulSoup(locations_page.text, features="lxml")
    for store in soup.find_all("item"):
        store_tags = store.find_all()
        store_dict = {}
        for tag in store_tags:
            store_dict[tag.name] = tag.getText()
        stores.append(store_dict)
    return stores


def extract_address(location: str):
    # split by comma
    location_split = location.split(",")
    # define two parts of string
    location_front = location_split[0]
    location_back = (location_split[1]).strip()
    # split front by last space
    split_front = location_front.rsplit(" ", 1)
    address = split_front[0]
    city = split_front[1]
    # split back into two
    location_back_split = location_back.split(" ")
    state = location_back_split[0]
    zip_code = location_back_split[1]
    return {"address": address, "city": city, "state": state, "zip_code": zip_code}


def extract_horus(operatinghours: str):
    # replace xml tags with space
    hours = regEx.sub(r"<[^>]*>", " ", operatinghours).strip()
    return hours


def transform_record(raw: Any) -> SgRecord:
    address_dict = extract_address(raw["address"])
    return SgRecord(
        page_url=f"{domain}/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php",
        location_type=SgRecord.MISSING,
        locator_domain=domain,
        location_name=raw["location"],
        street_address=address_dict["address"],
        city=address_dict["city"],
        state=address_dict["state"],
        zip_postal=address_dict["zip_code"],
        country_code=raw["country"],
        phone=raw["telephone"],
        latitude=raw["latitude"],
        longitude=raw["longitude"],
        hours_of_operation=extract_horus(raw["operatinghours"]),
        store_number=raw["storeid"],
        raw_address=raw["address"],
    )


if __name__ == "__main__":
    logger.info(f"starting scrape for {domain}")
    with SgWriter() as writer:
        results = fetch_raw_using()
        [
            writer.write_row(transform_record(indiv_record))
            for record in results
            for indiv_record in record
        ]
    logger.info("scrape complete")
