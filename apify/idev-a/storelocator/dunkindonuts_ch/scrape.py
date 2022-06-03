from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkindonuts.ch"
base_url = "https://www.dunkindonuts.ch/storefinder"
json_url = "https://storerocket.io/api/user/{}/locations?radius=2000&units=kilometers"


def fetch_data():
    with SgRequests() as session:
        key = bs(session.get(base_url, headers=_headers).text, "lxml").select_one(
            "div#storerocket-widget"
        )["data-storerocket-id"]
        locations = session.get(json_url.format(key), headers=_headers).json()[
            "results"
        ]["locations"]
        for _ in locations:
            if "Coming Soon" in _["name"]:
                continue
            street_address = _["address"].split(",")[0]
            page_url = f"https://www.dunkindonuts.ch/storefinder?location={_['slug']}"
            hours = []
            for day, hh in _.get("hours", {}).items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                location_type=_["location_type_name"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
