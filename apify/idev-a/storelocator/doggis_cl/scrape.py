from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import ssl
import time
import json
from webdriver_manager.chrome import ChromeDriverManager

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.doggis.cl"
base_url = "https://www.doggis.cl/locales"
json_url = "operationName=getStoresZones"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    rr = driver.wait_for_request(json_url, timeout=30)
    time.sleep(20)
    locations = json.loads(rr.response.body)["data"]["stores"]["items"]
    for _ in locations:
        addr = _["address"]
        hours = []
        for hh in _.get("humanSchedule", []):
            hours.append(f"{hh['days']}: {hh['schedule']}")
        raw_address = addr["address"] + " " + addr["addressSecondary"]
        _addr = parse_address_intl(raw_address)
        yield SgRecord(
            page_url=base_url,
            location_name=_["name"],
            street_address=addr["address"],
            city=_addr.city,
            state=_addr.state,
            country_code="Chile",
            phone=_["phone"],
            latitude=addr["location"]["lat"],
            longitude=addr["location"]["lng"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=raw_address,
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
