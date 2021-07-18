from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
import time
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
    locator_domain = "https://www.tealsmarket.com/"
    base_url = "https://www.tealsmarket.com/my-store/store-locator"
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if (
                    rr.url.startswith("https://api.freshop.com/1/stores?app_key")
                    and rr.response
                ):
                    exist = True
                    url = f'https://api.freshop.com/1/stores?app_key=teals_iga&has_address=true&limit=-1&token={rr.url.split("token=")[1]}'
                    with SgRequests() as session:
                        locations = session.get(url, headers=_headers).json()
                        for _ in locations["items"]:
                            yield SgRecord(
                                page_url=_["url"],
                                location_name=_["name"],
                                store_number=_["number"],
                                street_address=_["address_1"],
                                city=_["city"],
                                state=_["state"],
                                zip_postal=_["postal_code"],
                                latitude=_["latitude"],
                                longitude=_["longitude"],
                                country_code=_["country"],
                                phone=_["phone"].split("\n")[0],
                                locator_domain=locator_domain,
                                hours_of_operation=_["hours_md"].replace("\n", "; "),
                            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
