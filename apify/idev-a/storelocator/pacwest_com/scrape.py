from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
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
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "www.pacwest.com",
    "Referer": "https://www.pacwest.com/branch",
    "Cookie": "visid_incap_2002375=6+sMlVbsRxKzY/GJ/7bV33qeWGEAAAAAQUIPAAAAAABC2zU3mM04ZTIAN1DP4WGV; nlbi_2002375=CxTPc0Zdx0cbGYBfcwum1QAAAACyTeUGRlMHsNUlPjJ7UGSk; incap_ses_538_2002375=yJttCTvr+yU7+J9qn1x3B3qeWGEAAAAAqDtgGLYdH78qlc2eZNVqMQ==; maxmind={%22city%22:%22Los%20Angeles%22%2C%22country%22:%22United%20States%22%2C%22zip%22:%2290045%22%2C%22lat%22:33.956%2C%22lng%22:-118.3887%2C%22state%22:%22CA%22%2C%22tag%22:%22cookies:maxmind:af739dca3f867115b0c730f8e00860d3%22}; _ga=GA1.2.55103594.1633197696; _gid=GA1.2.547868715.1633197696; _gat_gtag_UA_137967974_1=1; nmstat=efe5004d-e020-c5a3-dd37-4fb3923622a2; __hstc=53759287.2feec882bb3673281a1225392b735ac5.1633197699406.1633197699406.1633197699406.1; hubspotutk=2feec882bb3673281a1225392b735ac5; __hssrc=1; __hssc=53759287.1.1633197699407; OptanonAlertBoxClosed=2021-10-02T18:01:51.872Z; OptanonConsent=isIABGlobal=false&datestamp=Sat+Oct+02+2021+11%3A01%3A51+GMT-0700+(Pacific+Daylight+Time)&version=6.8.0&hosts=&consentId=8d377fa5-3e22-4d64-a3ea-8f83c091281a&interactionCount=1&landingPath=NotLandingPage&groups=C0003%3A1%2CC0001%3A1%2CC0002%3A1%2CC0004%3A1%2CBG2%3A1",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pacwest.com"
base_url = "https://www.pacwest.com/api/locations"


def fetch_data():
    with SgChrome() as driver:
        driver.get(locator_domain)
        cookies = []
        for cookie in driver.get_cookies():
            cookies.append(f"{cookie['name']}={cookie['value']}")
        _headers["Cookie"] = "; ".join(cookies)
        with SgRequests(verify_ssl=False) as session:
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                street_address = _["street"]
                if _["street2"]:
                    street_address += " " + _["street2"]
                location_type = ",".join(_["type"])
                if "branch" not in location_type:
                    continue
                hours = []
                for hh in _.get("hours", []):
                    hours.append(f"{hh['day']}: {hh['time']}")
                yield SgRecord(
                    page_url="https://www.pacwest.com/branch",
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="US",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
