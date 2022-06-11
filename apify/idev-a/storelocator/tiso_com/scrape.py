from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tiso.com"
base_url = "https://apps.tiso.com/datafeeds/shop_hours/hours.php"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["locations"]
        for _ in locations:
            addr = _["address"].split(",")
            location_type = ""
            if _["temporary_closure"]:
                location_type = "temporary_closure"
            hours = []
            for day, hh in _["hours"].items():
                hours.append(f"{day}: {hh['open']} - {hh['close']}")
            yield SgRecord(
                page_url=_["url"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=", ".join(addr[:-2]),
                city=addr[-2],
                zip_postal=addr[-1],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="UK",
                phone=_["telephone"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
