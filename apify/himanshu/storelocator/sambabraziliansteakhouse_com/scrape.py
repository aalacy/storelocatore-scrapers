import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://www.sambabraziliansteakhouse.com/"
    locator_domain = base_url
    r = session.get("https://www.sambabraziliansteakhouse.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find_all("script", {"type": "application/ld+json"})[-1]
    l1 = json.loads(script.contents[0])
    location_name = l1["name"]
    street_address = l1["address"]["streetAddress"]
    city = l1["address"]["addressLocality"]
    state = l1["address"]["addressRegion"]
    zip_code = l1["address"]["postalCode"]
    country_code = "US"
    store_number = ""
    phone = l1["telephone"]
    location_type = "<MISSING>"
    latitude = re.findall(r'lat":[0-9]{2}\.[0-9]+', str(soup))[0].split(":")[1]
    longitude = re.findall(r'lng":-[0-9]{2,3}\.[0-9]+', str(soup))[0].split(":")[1]
    hours_of_operation = (
        " ".join(l1["openingHours"])
        .replace("Su", "Sun")
        .replace("Mo", "Mon")
        .replace("Tu", "Tue")
        .replace("We", "Wed")
        .replace("Th", "Thu")
        .replace("Fr", "Fri")
        .replace("Sa", "Sat")
        .strip()
    )

    sgw.write_row(
        SgRecord(
            locator_domain=locator_domain,
            page_url=base_url,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
