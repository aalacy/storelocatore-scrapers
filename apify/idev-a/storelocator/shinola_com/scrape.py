from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
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
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://www.shinola.com/store-locator",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.shinola.com/"
    base_url = "https://www.shinola.com/store-locator/"
    json_url = "https://www.shinola.com/rest/all/V1/bedrock/storeLocator/search/0/1/%5B%5D/1/%5B%5D/1"
    with SgChrome() as driver:
        driver.get(base_url)
        with SgRequests() as session:
            cookies = []
            for cookie in driver.get_cookies():
                cookies.append(f"{cookie['name']}={cookie['value']}")
            _headers["cookie"] = "; ".join(cookies)
            locations = session.get(json_url, headers=_headers).json()
            for _ in locations["locations"]:
                if "Shinola" not in _["name"]:
                    continue
                page_url = base_url + _["url_key"]
                hours = []
                times = "closed"
                if _["monday_enable"]:
                    times = f"{_['monday_open']}-{_['monday_close']}"
                hours.append(f"Mon: {times}")
                times = "closed"
                if _["tuesday_enable"]:
                    times = f"{_['tuesday_open']}-{_['tuesday_close']}"
                hours.append(f"Tue: {times}")
                times = "closed"
                if _["wednesday_enable"]:
                    times = f"{_['wednesday_open']}-{_['wednesday_close']}"
                hours.append(f"Wed: {times}")
                times = "closed"
                if _["thursday_enable"]:
                    times = f"{_['thursday_open']}-{_['thursday_close']}"
                hours.append(f"Thu: {times}")
                times = "closed"
                if _["friday_enable"]:
                    times = f"{_['friday_open']}-{_['friday_close']}"
                hours.append(f"Fri: {times}")
                times = "closed"
                if _["saturday_enable"]:
                    times = f"{_['saturday_open']}-{_['saturday_close']}"
                hours.append(f"Sat: {times}")
                times = "closed"
                if _["sunday_enable"]:
                    times = f"{_['sunday_open']}-{_['sunday_close']}"
                hours.append(f"Sun: {times}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["location_id"],
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["region"],
                    zip_postal=_["postcode"],
                    country_code=_["country_id"],
                    phone=_["phone"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
