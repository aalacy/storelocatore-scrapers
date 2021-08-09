from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("fatburger")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://fatburger.com/"
base_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=BBOAPSVZOXCPKFUV&center=33.6611,-117.673&coordinates=32.8572717922566,-116.29421582031239,34.45748789640378,-119.05178417968746&multi_account=true&page={page}&pageSize=1000"
days = [
    "",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            locations = session.get(base_url.format(page), headers=_headers).json()
            if not locations:
                break
            page += 1
            for store in locations:
                if store["status"] != "open":
                    continue
                _ = store["store_info"]
                street_address = _["address"]
                if _["address_extended"]:
                    street_address += " " + _["address_extended"]
                hours = []
                if _.get("store_hours"):
                    for hh in _["store_hours"].split(";"):
                        hr = hh.split(",")
                        hours.append(f"{days[hr]}: {_time(hr[1])}-{_time(hr[2])}")
                yield SgRecord(
                    page_url=_["website"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["locality"],
                    state=_["region"],
                    zip_postal=_["postcode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["country"],
                    phone=_["phone"],
                    location_type=["brand_name"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
