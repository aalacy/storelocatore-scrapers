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
    locator_domain = "https://www.fairplayfoods.com/"
    base_url = "https://www.fairplayfoods.com/my-store/store-locator"
    json_url = "https://api.freshop.com/1/stores?app_key=fairplay_foods"
    with SgChrome() as driver:
        with SgRequests() as session:
            driver.get(base_url)
            exist = False
            while not exist:
                time.sleep(1)
                for rr in driver.requests:
                    if rr.url.startswith(json_url) and rr.response:
                        exist = True
                        token = rr.url.split("&token=")[1]
                        locations = session.get(
                            f"https://api.freshop.com/1/stores?app_key=fairplay_foods&has_address=true&is_selectable=true&limit=-1&token={token}"
                        ).json()
                        for _ in locations["items"]:
                            street_address = _["address_1"]
                            yield SgRecord(
                                page_url=_["url"],
                                location_name=_["name"],
                                store_number=_["store_number"],
                                street_address=street_address,
                                city=_["city"],
                                state=_["state"],
                                zip_postal=_["postal_code"],
                                latitude=_["latitude"],
                                longitude=_["longitude"],
                                country_code=_["country"],
                                phone=_["phone"],
                                locator_domain=locator_domain,
                                hours_of_operation=_["hours_md"]
                                .replace("\n", ";")
                                .strip(),
                            )

                        break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
