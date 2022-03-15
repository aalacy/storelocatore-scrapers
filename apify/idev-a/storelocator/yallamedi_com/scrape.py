from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("yallamedi")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://yallamedi.com/"
base_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=LWNLRVTLHRRHVYID&center=33.6611,-117.673&coordinates=0.85727179225715,-90.0,90.0,-180.0&multi_account=false&page={}&pageSize=100"
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
                        if not hh:
                            continue
                        hr = hh.split(",")
                        hours.append(f"{hr_obj[hr[0]]}: {_time(hr[1])}-{_time(hr[2])}")
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
                    location_type=_["brand_name"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
