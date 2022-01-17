from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgselenium import SgChrome
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from bs4 import BeautifulSoup as bs
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("")


locator_domain = "https://www.bupa.co.uk"
base_url = "https://www.bupa.co.uk/dental/dental-care/practices?loc={}"
bs_url = "https://www.bupa.co.uk/BDC/SearchPractices"
json_url = "https://www.bupa.co.uk/BDC/GoogleMapSearch"


def fetch_records(driver, http, search):
    for zip in search:
        del driver.requests
        headers = {}
        driver.get(
            f'https://www.bupa.co.uk/dental/dental-care/practices?loc={zip.replace(" ", "%20")}'
        )
        try:
            rr = driver.wait_for_request(json_url, timeout=30)
        except:
            continue

        for key, val in rr.headers.items():
            if key != "content-length":
                headers[key] = val
        page = 1
        payload = json.loads(rr.body)
        while True:
            payload["pageIndex"] = page
            locations = bs(
                http.post(bs_url, headers=headers, json=payload).text, "lxml"
            ).select("div.centervalign-outerwrapper")
            if locations:
                page += 1
            else:
                break
            locs = http.post(json_url, headers=headers, json=payload).json()
            payload["dataCount"] += len(locs)
            logger.info(f"[{zip}] {len(locations)}")
            for x, _ in enumerate(locs):
                page_url = locator_domain + _["PageUrl"]
                addr = _["FullAddress"].split(",")
                info = locations[x]
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in info.select("div.opening-hours-container table tbody tr")
                ]
                phone = ""
                if info.select_one("a.tel-number"):
                    phone = info.select_one("a.tel-number").text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["PageTitle"],
                    street_address=", ".join(addr[:-2]),
                    city=addr[-2],
                    zip_postal=_["PostalCode"],
                    country_code="uk",
                    phone=phone,
                    latitude=_["Latitude"],
                    longitude=_["Longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=_["FullAddress"],
                )


if __name__ == "__main__":
    with SgChrome() as driver:
        with SgRequests() as http:
            search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])
            with SgWriter(
                SgRecordDeduper(
                    SgRecordID({SgRecord.Headers.RAW_ADDRESS}),
                    duplicate_streak_failure_factor=100,
                )
            ) as writer:
                for rec in fetch_records(driver, http, search):
                    writer.write_row(rec)
