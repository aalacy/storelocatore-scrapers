from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("johnnyrockets")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "origin": "https://locations.johnnyrockets.com",
    "referer": "https://locations.johnnyrockets.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.johnnyrockets.com/"
base_url = "https://locations.johnnyrockets.com/site-map/all"
MISSING = SgRecord.MISSING
hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def _u(url):
    return (
        url.split("#")[0]
        .replace("+~", "%26")
        .replace("-", "+")
        .replace("_", ".")
        .replace("~", "-")
        .replace("*", ",")
        .replace("'", "%27")
    )


def fetch_data():
    with SgRequests() as session:
        app_url = (
            "https://locations.johnnyrockets.com/"
            + bs(session.get(base_url, headers=_headers).text, "lxml").find_all(
                "script"
            )[-1]["src"]
        )
        token = (
            session.get(app_url, headers=_headers)
            .text.split('constant("API_TOKEN",')[1]
            .split(")")[0][1:-1]
        )
        json_url = f"https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token={token}&multi_account=true"
        locations = session.get(json_url, headers=_headers).json()["locations"]
        logger.info(f"{len(locations)} found")
        header1["authorization"] = token
        for store in locations:
            if store["open_or_closed"] != "open":
                location_type = "Temporarily Closed"
            else:
                location_type = MISSING
            url = store["llp_url"].split("/")
            street = _u(url[-1])
            locality = _u(url[-2])
            region = _u(url[-3])
            j_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?address={street}&locality={locality}&multi_account=true&pageSize=30&region={region}"
            logger.info(j_url)
            for loc in session.get(j_url, headers=header1).json():
                try:
                    _ = loc["store_info"]
                except:
                    continue
                street_address = _["address"]
                if _["address_extended"]:
                    street_address += " " + _["address_extended"]
                if _.get("address_3"):
                    street_address += " " + _["address_3"]
                hours = []
                if _.get("store_hours"):
                    for hh in _["store_hours"].split(";"):
                        if not hh:
                            continue
                        hr = hh.split(",")
                        hours.append(f"{hr_obj[hr[0]]}: {_time(hr[1])}-{_time(hr[2])}")
                yield SgRecord(
                    page_url=_["website"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["locality"],
                    state=_.get("region"),
                    zip_postal=_.get("postcode"),
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["country"],
                    phone=_["phone"],
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
