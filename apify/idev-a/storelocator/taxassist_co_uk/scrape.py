from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("taxassist")


_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}
locator_domain = "https://www.taxassist.co.uk/"
base_url = "https://www.taxassist.co.uk/locations"


def _fix(original):
    regex = re.compile(r'\\(?![/u"])')
    return regex.sub(r"\\\\", original).replace("\t", "").replace("\n", "")


def record_initial_requests(http: SgRequests):
    soup = bs(http.get(base_url, headers=_headers).text, "lxml")
    links = [link["href"] for link in soup.select("main div.row a.primary.outline")]
    logger.info(f"{len(links)} found")
    for page_url in links:
        sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
        details = [dd["href"] for dd in sp1.select("main div.mt-auto a.outline")]
        if details:
            for url in details:
                yield fetch_records(http, url)
        else:
            yield fetch_records(http, page_url)


def fetch_records(http, page_url):
    logger.info(page_url)
    res = http.get(page_url)
    if res.status_code != 200:
        return None
    sp2 = bs(res.text, "lxml")
    raw_address = " ".join(sp2.address.stripped_strings)
    if "coming soon" in raw_address.lower():
        return None

    location = json.loads(
        _fix(sp2.find("script", type="application/ld+json").string.strip())
    )
    if location["address"]["streetAddress"] == "Coming Soon":
        return None
    addr = parse_address_intl(raw_address + ", United Kingdom")
    city = addr.city
    if not city:
        city = raw_address.split(",")[-2]
    else:
        if city.lower() in location["address"]["postalCode"].lower():
            city = raw_address.split(",")[-2]
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    if location["address"]["streetAddress"] == "M25 Business centre":
        street_address = (
            location["address"]["streetAddress"]
            + " "
            + location["address"]["addressLocality"]
        )
    hours = []
    for _ in location["openingHoursSpecification"]:
        hour = f"{_['opens']}-{_['closes']}"
        if hour == "00:00-00:00":
            hour = "closed"
        hours.append(f"{_['dayOfWeek']}: {hour}")
    hours_of_operation = "; ".join(hours)
    if re.search(r"please contact", hours_of_operation, re.IGNORECASE):
        hours_of_operation = ""

    return SgRecord(
        page_url=page_url,
        location_type=location["@type"],
        location_name=location["name"],
        street_address=street_address,
        city=city,
        zip_postal=location["address"]["postalCode"],
        country_code="uk",
        latitude=location["geo"]["latitude"],
        longitude=location["geo"]["longitude"],
        phone=location["telephone"],
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            results = record_initial_requests(http)
            for rec in results:
                if rec:
                    writer.write_row(rec)
