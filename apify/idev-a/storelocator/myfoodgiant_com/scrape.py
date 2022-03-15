from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import time
import json
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

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://myfoodgiant.com/"
    page_url = "https://myfoodgiant.com/find-your-store/"
    json_url = "https://myfoodgiant.com/wp-json/wpgmza/v1/marker-listing/"
    with SgChrome() as driver:
        driver.get(page_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if rr.url.startswith(json_url) and rr.response:
                    exist = True
                    driver.get(rr.url)
                    locations = json.loads(bs(driver.page_source, "lxml").text.strip())[
                        "meta"
                    ]
                    for _ in locations:
                        addr = _["address"].split(",")
                        yield SgRecord(
                            page_url=page_url,
                            store_number=_["id"],
                            location_name=_["title"],
                            street_address=addr[0].strip(),
                            city=addr[1].strip(),
                            state=addr[2].strip().split(" ")[0].strip(),
                            zip_postal=addr[2].strip().split(" ")[-1].strip(),
                            latitude=_["lat"],
                            longitude=_["lng"],
                            country_code="US",
                            locator_domain=locator_domain,
                        )

                    break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
