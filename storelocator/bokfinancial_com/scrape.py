from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
import time
import us
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("bokfinancial")

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-Type": "application/json; charset=utf-8",
    "Host": "bok-dashboard.golocalinteractive.com",
    "Origin": "https://locations.bokfinancial.com",
    "Referer": "https://locations.bokfinancial.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://locations.bokfinancial.com/"
    base_url = "https://locations.bokfinancial.com/bank-locations"
    json_url = "https://bok-dashboard.golocalinteractive.com/api/v1/bokfin/locations"
    key_url = "https://bok-dashboard.golocalinteractive.com/api/v1/bokfin/locations/geocode/{}/200/all?_=1624301775994"
    stores = []
    with SgChrome() as driver:
        with SgRequests() as session:
            driver.get(base_url)
            driver.find_element_by_css_selector(
                'span.input-group-btn button[type="submit"]'
            ).click()
            exist = False
            while not exist:
                time.sleep(1)
                for rr in driver.requests:
                    if rr.url.startswith(json_url) and rr.response:
                        exist = True
                        _headers["Authorization"] = rr.headers["Authorization"]
                        total = 0
                        for state in us.states.STATES:
                            locations = session.get(
                                key_url.format(state.name), headers=_headers
                            ).json()
                            total += len(locations)
                            logger.info(
                                f"[total {total}] [{state.name}] {len(locations)} found"
                            )
                            for _ in locations:
                                location_type = _["type"]
                                if location_type == "ATM":
                                    continue
                                street_address = _["address"]
                                if _["address_2"]:
                                    street_address += " " + _["address_2"]
                                page_url = f"https://locations.bokfinancial.com/bank-locations/{_['state']}/{_['city']}/{street_address.replace(' ','-')}/{_['id']}"
                                if _["id"] in stores:
                                    continue
                                stores.append(_["id"])
                                hours = []
                                hours.append(f"Mo: {_['mo_open']}-{_['mo_close']}")
                                hours.append(f"Tu: {_['tu_open']}-{_['tu_close']}")
                                hours.append(f"We: {_['we_open']}-{_['we_close']}")
                                hours.append(f"Th: {_['th_open']}-{_['th_close']}")
                                hours.append(f"Fr: {_['fr_open']}-{_['fr_close']}")
                                if _["sa_open"]:
                                    hours.append(f"Sa: {_['sa_open']}-{_['sa_close']}")
                                else:
                                    hours.append("Sa: closed")
                                if _["su_open"]:
                                    hours.append(f"Su: {_['su_open']}-{_['su_close']}")
                                else:
                                    hours.append("Su: closed")

                                yield SgRecord(
                                    page_url=page_url,
                                    store_number=_["id"],
                                    location_name=_["name"],
                                    street_address=street_address,
                                    city=_["city"],
                                    state=_["state"],
                                    zip_postal=_["zipcode"],
                                    latitude=_["latitude"],
                                    longitude=_["longitude"],
                                    country_code="US",
                                    phone=_["contact_phone"],
                                    location_type=location_type,
                                    locator_domain=locator_domain,
                                    hours_of_operation="; ".join(hours),
                                )

                        break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
