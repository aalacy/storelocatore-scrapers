from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import json
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.eurochange.co.uk"
base_url = "https://www.eurochange.co.uk/branches/GetBranches/51.5073509/-0.1277583?Latitude=51.5073509&longitude=-0.1277583"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _v(val):
    return val.replace("&#44;", ",").strip()


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    driver.wait_for_request("https://www.eurochange.co.uk/branches/GetBranches/")
    locations = json.loads(bs(driver.page_source, "lxml").text)
    for _ in locations:
        if _["ComingSoon"] != "N":
            continue
        page_url = f"https://www.eurochange.co.uk/branches/{_['SEOBranchNameLink']}"
        raw_address = _v(
            f"{_['AddressLine1']}, {_['AddressLine2']}, {_['AddressLine3']}, UK"
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hours = []
        if _["Open24Hours"] == "N":
            for day in days:
                _day = day.lower()
                if _.get(f"{_day}Opening"):
                    start = _.get(f"{_day}Opening")
                    end = _.get(f"{_day}Closing")
                    if start == "Closed":
                        times = "Closed"
                    else:
                        times = f"{start} - {end}"
                    hours.append(f"{day}: {times}")
        else:
            hours = ["Open 24 hours"]
        yield SgRecord(
            page_url=page_url,
            store_number=_["BranchId"],
            location_name=_["BranchName"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=_["Postcode"],
            latitude=_["Latitude"],
            longitude=_["Longitude"],
            country_code="UK",
            phone=_.get("TelephoneNo"),
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
