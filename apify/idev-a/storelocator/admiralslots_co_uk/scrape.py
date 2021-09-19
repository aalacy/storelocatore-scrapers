from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.admiralslots.co.uk"
base_url = "https://www.admiralslots.co.uk/venues.json"
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = "https://www.admiralslots.co.uk/venue/" + _["link"]
            hours = []
            for day, times in _.items():
                if day.lower() in days:
                    hours.append(f"{day}: {times}")
            phone = _["telephone"]
            if phone == "TBC":
                phone = ""
            raw_address = f"{_['address']}, {_['city']}, United Kingdom"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=_["postcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
