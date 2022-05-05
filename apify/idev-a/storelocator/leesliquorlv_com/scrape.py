from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import os
import time

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"

import json

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://shop.leesdiscountliquor.com",
    "referer": "https://shop.leesdiscountliquor.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://leesdiscountliquor.com/"
start_url = "https://shop.leesdiscountliquor.com/buy-alcohol"
base_url = "https://liquorapps.com/Bcapi/api/Store/StoreGetList"
detail_url = "https://liquorapps.com/Bcapi/api/Store/StoreGetDetail"
login_url = "https://liquorapps.com/Bcapi/api/Login/LoginCustomer"


def _sessionId(session, old_json, StoreId):
    json_data = {
        "AppId": 11137,
        "AppVersion": "12.1",
        "DeviceId": old_json["DeviceId"],
        "DeviceType": "W",
        "EmailId": "",
        "LoginType": "B",
        "Password": "",
        "StoreId": StoreId,
        "SourceId": "",
        "SessionId": old_json["DeviceId"],
        "UserId": "",
        "UserIp": "",
    }
    data = session.post(login_url, headers=_headers, json=json_data).json()
    return data


def fetch_data():
    with SgRequests() as session:
        with SgChrome(executable_path=ChromeDriverManager().install()) as driver:
            driver.get(start_url)
            time.sleep(10)
            locations = []
            SessionId = ""
            json_data = {}
            for rr in driver.requests[::-1]:
                if rr.url == base_url and not locations:
                    locations = json.loads(rr.response.body)["ListStore"]
                if rr.url == login_url and not SessionId:
                    SessionId = json.loads(rr.response.body)["SessionId"]
                    json_data = json.loads(rr.response.body)

            for loc in locations:
                if "coming soon" in loc["Location"].lower():
                    continue
                logger.info(loc["StoreId"])
                json_data["StoreId"] = loc["StoreId"]
                json_data = _sessionId(session, json_data, loc["StoreId"])

                _ = session.post(detail_url, headers=_headers, json=json_data).json()[
                    "GetStoredetails"
                ]
                street_address = _["Address1"]
                if _["Address2"]:
                    street_address += " " + _["Address2"]

                hours = []
                for hh in _.get("ListStoreTime", []):
                    hours.append(
                        f"{hh['DayID']}: {hh['StoreOpenTime']} - {hh['StoreCloseTime']}"
                    )
                yield SgRecord(
                    page_url=start_url,
                    store_number=loc["StoreId"],
                    location_name=_["StoreName"],
                    street_address=street_address,
                    city=_["City"],
                    state=_["State"],
                    zip_postal=_["Zip"],
                    latitude=_["Latitude"],
                    longitude=_["Longitude"],
                    country_code="US",
                    phone=_["ContactNo"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
