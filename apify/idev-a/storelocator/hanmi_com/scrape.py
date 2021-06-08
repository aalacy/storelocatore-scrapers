from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from selenium.webdriver.common.keys import Keys
import json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
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


def _time(start, end):
    times = "closed"
    if start and end:
        times = f"{start}-{end}"
    return times


def fetch_data():
    locator_domain = "https://www.hanmi.com/"
    json_url = "https://hosted.where2getit.com/hanmi/rest/locatorsearch"
    page_url = "https://www.hanmi.com/about-us/locations"
    with SgChrome() as driver:
        driver.get(page_url)
        driver.find_element_by_css_selector("button.set-location").click()
        driver.switch_to.frame("bfy_iframe")
        driver.find_element_by_css_selector("input#search_input").send_keys(
            "90006", Keys.ENTER
        )
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//ul/li[@class="poi-item"]'))
        )
        driver.switch_to.default_content()
        appkey = ""
        for rr in driver.requests:
            if rr.url.startswith(json_url):
                appkey = json.loads(rr.body)["request"]["appkey"]
        with SgRequests(proxy_rotation_failure_threshold=1) as session:
            payload = {
                "request": {
                    "appkey": appkey,
                    "formdata": {
                        "geoip": "start",
                        "dataview": "store_default",
                        "limit": "1000",
                        "geolocs": {
                            "geoloc": [
                                {
                                    "addressline": "",
                                    "country": "",
                                    "latitude": "",
                                    "longitude": "",
                                }
                            ]
                        },
                        "searchradius": "5000",
                        "where": {
                            "internalname": {"ne": "ATM"},
                            "or": {"atm": {"ilike": ""}, "branch_type": {"eq": ""}},
                        },
                    },
                    "geoip": "1",
                }
            }
            locations = session.post(json_url, headers=_headers, json=payload).json()
            for _ in locations["response"]["collection"]:
                street_address = _["address1"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                hours = []
                hours.append(f"Mon: {_time(_['mon_open'], _['mon_close'])}")
                hours.append(f"Tue: {_time(_['tues_open'], _['tues_close'])}")
                hours.append(f"Wed: {_time(_['wed_open'], _['wed_close'])}")
                hours.append(f"Thu: {_time(_['thurs_open'], _['thurs_close'])}")
                hours.append(f"Fri: {_time(_['fri_open'], _['fri_close'])}")
                hours.append(f"Sat: {_time(_['sat_open'], _['sat_close'])}")
                hours.append(f"Sun: {_time(_['sun_open'], _['sun_close'])}")
                page_url = f"https://locations.hanmi.com/{_['state'].lower()}/{'-'.join(_['city'].lower().strip().split(' '))}/{_['clientkey']}/"
                res = session.get(page_url, headers=_headers)
                if res.status_code != 200:
                    continue
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["clientkey"],
                    location_name=_["internalname"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["postalcode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["country"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
