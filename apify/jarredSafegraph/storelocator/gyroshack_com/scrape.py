import re as regEx
from typing import Any

from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgrequests.sgrequests import SgRequestsBase
from sgscrape.sgpostal import USA_Best_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter


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

    with SgRequests() as http:
        locations_page = SgRequestsBase.raise_on_err(
            http.request(
                f"{domain}wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php",
                headers=headers,
            )
        )

        soup = BeautifulSoup(locations_page.text, features="lxml")
        for store in soup.find_all("item"):
            yield xml_to_dict(store)


def xml_to_dict(store) -> dict:
    store_tags = store.find_all()
    store_dict = {}
    for tag in store_tags:
        store_dict[tag.name] = tag.getText()
    return store_dict


def extract_address(location: str):
    parse_address_usa = parse_address(USA_Best_Parser(), location)
    address = f"{parse_address_usa.street_address_1} {parse_address_usa.street_address_2}".replace(
        "None", ""
    ).strip()
    return {
        "address": address,
        "city": parse_address_usa.city,
        "state": parse_address_usa.state,
        "zip_code": parse_address_usa.postcode,
    }


def extract_hours(operatinghours: str):
    if operatinghours is not None:
        operatinghours = operatinghours.replace("\n", "")
        operatinghours = operatinghours.replace("\r", "")
        internal_br = "(?<=[a-zA-Z])<br>(?=[a-zA-Z])"
        hours = regEx.sub(internal_br, ", ", operatinghours).strip()
        tags = regEx.compile("<.*?>")
        hours = regEx.sub(tags, " ", hours).strip()
        double_space = regEx.compile("  ")
        hours = regEx.sub(double_space, ", ", hours).strip()
        return hours
    else:
        return ""


def transform_record(raw: Any) -> SgRecord:
    address_dict = extract_address(raw.get("address"))
    return SgRecord(
        page_url=SgRecord.MISSING,
        location_type=SgRecord.MISSING,
        locator_domain=domain,
        location_name=raw.get("location"),
        street_address=address_dict.get("address"),
        city=address_dict.get("city"),
        state=address_dict.get("state"),
        zip_postal=address_dict.get("zip_code"),
        country_code=raw.get("country"),
        phone=raw.get("telephone"),
        latitude=raw.get("latitude"),
        longitude=raw.get("longitude"),
        hours_of_operation=extract_hours(raw.get("operatinghours")),
        store_number=raw.get("storeid"),
        raw_address=raw.get("address"),
    )


if __name__ == "__main__":
    logger.info(f"starting scrape for {domain}")
    deduper = SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    with SgWriter(deduper) as writer:
        for record in fetch_raw_using():
            writer.write_row(transform_record(record))
    logger.info("scrape complete")
