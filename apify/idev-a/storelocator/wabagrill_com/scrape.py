from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("wabagrill")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://wabagrill.com/"
base_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=KBAXTJEEPNAVUUJW&center=34.030532,-118.015502&coordinates=32.46870370507422,-116.39501860156292,35.56413211237127,-119.63598539843782&multi_account=false&page={}&pageSize=1000"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            locations = session.get(base_url.format(page), headers=_headers).json()
            if type(locations) != list:
                break
            if not locations:
                break
            logger.info(f"[page {page}] {len(locations)}")
            page += 1
            for loc in locations:
                _ = loc["store_info"]
                page_url = _.get("website")
                if not page_url:
                    page_url = f"https://locations.wabagrill.com/ll/{_['country']}/{_['region']}/{_['locality'].replace(' ','-')}/{_['address'].replace('.','_').replace(' ','-')}"
                street_address = _["address"]
                if _["address_extended"]:
                    street_address += " " + _["address_extended"]
                _tmp = []
                if _.get("store_hours"):
                    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    hours = _.get("store_hours").split(";")[:-1]
                    i = 0
                    for d in days:
                        try:
                            time = hours[i].split(",")
                        except IndexError:
                            i += 1
                            _tmp.append(f"{d}: Closed")
                            continue
                        start = f"{time[1][:2]}:{time[1][2:]}"
                        close = f"{time[2][:2]}:{time[2][2:]}"
                        _tmp.append(f"{d}: {start} - {close}")
                        i += 1
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["locality"],
                    state=_["region"],
                    zip_postal=_["postcode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["country"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(_tmp),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
