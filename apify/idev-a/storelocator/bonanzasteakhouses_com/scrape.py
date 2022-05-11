from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pon-bon.com/"
base_url = "https://pon-bon.com/locations"


def fetch_data():
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        user_id = sp1.select_one("div#storerocket-widget")["data-storerocket-id"]
        json_url = f"https://storerocket.io/api/user/{user_id}/locations?radius=500&units=miles"
        locations = session.get(json_url, headers=_headers).json()["results"][
            "locations"
        ]
        for _ in locations:
            street_address = _["address_line_1"]
            if _["address_line_2"]:
                street_address += " " + _["address_line_2"]
            page_url = base_url + "?location=" + _["slug"]
            hours = []
            for day, hh in _.get("hours", {}).items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_.get("state"),
                zip_postal=_["postcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=_["location_type_name"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
