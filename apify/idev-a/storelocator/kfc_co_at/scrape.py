from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kfc.co.at"
base_url = "https://kfc.co.at/restaurants"
json_url = "https://kfc.co.at/api/collections/shops/entries"


def fetch_data():
    with SgRequests() as session:
        _headers["x-xsrf-token"] = session.get(
            base_url, headers=_headers
        ).cookies.get_dict()["XSRF-TOKEN"]
        locations = session.get(json_url, headers=_headers).json()["data"]
        for _ in locations:
            hours = []
            for hh in _.get("opening_hours", []):
                times = "closed"
                if not hh["closed"]:
                    times = f"{hh['start']}-{hh['stop']}"
                hours.append(f"{hh['day_dayname']['label']}: {times}")
            yield SgRecord(
                page_url=_["permalink"],
                location_name=bs(_["title"], "lxml").text.strip(),
                street_address=" ".join(bs(_["street"], "lxml").stripped_strings),
                city=_["city"],
                zip_postal=_["zipcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Austria",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
