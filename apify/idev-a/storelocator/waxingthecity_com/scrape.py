from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.waxingthecity.com"
base_url = "https://www.waxingthecity.com/wp-content/uploads/locations.json"


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            cc = _["content"]
            street_address = cc["address"]
            if cc["address2"]:
                street_address += " " + cc["address2"]
            hours = []
            if type(cc["hours"]) == list:
                for hh in cc["hours"]:
                    hours.append(
                        f"{hh['dayOfWeek']}: {_time(hh['openTime'])}-{_time(hh['closeTime'])}"
                    )
            page_url = f"https://www.waxingthecity.com/locations/{cc['number']}/{cc['country']}/{cc['state_abbr']}/{cc['city']}/".lower()
            yield SgRecord(
                page_url=page_url,
                location_name=cc["title"],
                street_address=street_address,
                city=cc["city"],
                state=cc["state_abbr"],
                zip_postal=cc["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=cc["country"],
                phone=cc["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
