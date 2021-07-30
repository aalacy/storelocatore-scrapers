from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import time
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return val.strip().replace("–", "-")


def fetch_data():
    locator_domain = "https://www.donelans.com/"
    json_url = (
        "https://api.freshop.com/1/stores?app_key=donelans&has_address=true&limit=-1"
    )
    base_url = "https://www.donelans.com/my-store/store-locator"
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if rr.url.startswith(json_url) and rr.response:
                    exist = True
                    locations = json.loads(rr.response.body)
                    for _ in locations["items"]:
                        hours = []
                        for hh in _["hours_md"].split("\n\n"):
                            if "**" not in hh and "Senior" not in hh:
                                hours.append(hh)
                        yield SgRecord(
                            store_number=_["store_number"],
                            page_url=_["url"],
                            location_name=_["name"],
                            street_address=_["address_1"],
                            city=_["city"],
                            state=_["state"],
                            zip_postal=_["postal_code"],
                            country_code="US",
                            latitude=_["latitude"],
                            longitude=_["longitude"],
                            phone=_["phone_md"].split("\n")[0],
                            locator_domain=locator_domain,
                            hours_of_operation=_valid("; ".join(hours)),
                        )
                    break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
