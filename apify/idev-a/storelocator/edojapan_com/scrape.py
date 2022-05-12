from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

locator_domain = "https://www.edojapan.com/"
base_url = "https://www.edojapan.com/wp-json/edojapan/v1/locations"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            if "Opening Soon" in _["reason_closed"]:
                continue
            hours = []
            closed_cnt = 0
            for day, hh in _.get("hours", {}).items():
                if not hh.strip():
                    hh = "closed"
                    closed_cnt += 1
                hours.append(f"{day}: {hh}")
            location_type = ""
            if "Permanently Closed" in _["reason_closed"]:
                location_type = "Permanently Closed"
                hours = []
            elif closed_cnt == 7:
                hours = []
                location_type = "temporarily Closed"
            yield SgRecord(
                page_url=_["permalink"],
                store_number=_["storeNumber"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["province"],
                zip_postal=_["postal_code"],
                country_code=_["country"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["main_phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
