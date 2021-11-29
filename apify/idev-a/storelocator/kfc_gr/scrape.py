from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kfc.gr"
base_url = "https://www.kfc.gr/stores"

hr_obj = {
    "1": "Sunday",
    "2": "Monday",
    "3": "Tuesday",
    "4": "Wednesday",
    "5": "Thursday",
    "6": "Friday",
    "7": "Saturday",
}


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var siteSettings =")[1]
            .split("var siteLanguage")[0]
            .strip()[:-1]
        )["locations"]
        for _ in locations:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            location_type = ""
            if _["temporarily_closed"]:
                location_type = "temporarily closed"
            hours = []
            for hh in _.get("takeaway_schedule", []):
                hours.append(f"{hr_obj[hh['day']]}: {hh['from']}-{hh['to']}")
            city = addr.city
            if not city:
                _city = _["address"].split(",")[1].strip().split(" ")
                city = " ".join(_city[:-2])
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=city,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Greece",
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
