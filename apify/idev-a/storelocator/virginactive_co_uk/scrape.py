from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.virginactive.co.uk"
base_url = "https://www.virginactive.co.uk/api/club/getclubdetails"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"]["clubs"]
        for _ in locations:
            addr = parse_address_intl(_["compositeAddress"] + ", United Kingdom")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if not city:
                city = _["compositeAddress"].split(",")[-2].replace("Green", "").strip()
            hours = []
            for day, hh in _.get("openingHours", {}).items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=_["clubHomeUrl"],
                store_number=_["clubId"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="UK",
                phone=_["phoneNumber"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["compositeAddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
