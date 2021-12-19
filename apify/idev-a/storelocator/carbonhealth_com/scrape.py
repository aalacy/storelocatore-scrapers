from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def fetch_data():
    locator_domain = "https://carbonhealth.com/"
    base_url = "https://carbonhealth.com/locations"
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("script#__NEXT_DATA__")
            .string
        )
        for _ in locations["props"]["initialState"]["config"]["locations"]:
            if _.get("typ", "") == "Vaccination":
                continue
            page_url = locator_domain + _["slug"]
            hours = []
            temp = []
            for k, _hr in _["specialties"].items():
                if _hr["name"].lower() == "urgent care":
                    for hh in _hr["hours"]:
                        temp.append((hh["day"], f"{hh['from']}-{hh['to']}"))

            same = []
            diff = []
            _prev = ""
            for _hr in temp:
                day = _hr[0]
                hh = _hr[1]
                if day == 0:
                    diff.append((day, hh))
                    continue
                if same:
                    if _prev == hh:
                        same.append((day, hh))
                    else:
                        diff.append((day, hh))
                if not same:
                    _prev = hh
                    same.append((day, hh))

            same = sorted(same, key=lambda x: x[0])
            _days = [dd[0] for dd in same]
            if _days == range(7):
                hours.append(f"Everyday: {hh}")
            elif set(range(1, 6)).issubset(_days):
                hours.append(f"Weekdays: {hh}")
                for dd in same:
                    if dd[0] not in list(range(1, 6)):
                        hours.append(f"{days[dd[0]]}: {dd[1]}")
            for dd in diff:
                if dd[0] not in list(range(1, 6)):
                    hours.append(f"{days[dd[0]]}: {dd[1]}")

            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"]["firstLine"],
                city=_["address"]["city"],
                state=_["address"]["state"],
                zip_postal=_["address"]["zip"],
                latitude=_["address"]["latitude"],
                longitude=_["address"]["longitude"],
                country_code="US",
                phone=_.get("phoneNumber"),
                location_type=_.get("typ", ""),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
