from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.church-footwear.com/"
base_url = (
    "https://www.church-footwear.com/us/en/store-locator.glb.getAllStores.json?brand=CH"
)
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _d(_):
    hours = []
    if _.get("workingSchedule", {}):
        for day in days:
            day = day.lower()
            times = f"{_['workingSchedule'][day]}".strip()
            if times == "--":
                times = "closed"
            hours.append(f"{day}: {times}")

    state = _["stateOrProvinceName"]
    street_address = _["addressLine"][0].split("市")[-1].split("都")[-1].split("시")[-1]
    if state:
        if state == _["country"] or state.isdigit():
            state = ""
    if state and state in street_address:
        street_address = street_address.replace(state, "").strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
    hours_of_operation = " ".join(hours)
    if hours_of_operation.endswith(";"):
        hours_of_operation = hours_of_operation[:-1]
    return SgRecord(
        page_url="https://www.church-footwear.com/us/en/store-locator.html",
        store_number=_["uniqueID"],
        location_name=_["Description"]["displayStoreName"],
        street_address=street_address,
        city=_["city"],
        state=state,
        zip_postal=_.get("postalCode"),
        phone=_.get("telephone1"),
        latitude=_["latitude"],
        longitude=_["longitude"],
        country_code=_["country"],
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    with SgRequests() as http:

        locs = http.get(base_url, headers=_headers).json()
        for key, loc in locs.items():
            if type(loc) == dict:
                yield _d(loc)
            elif type(loc) == list:
                for _ in loc:
                    yield _d(_)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
