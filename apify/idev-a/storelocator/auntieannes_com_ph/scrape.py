from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://chekk.ph"
base_url = "https://chekk.ph/auntieannes#/"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("script#view-model")
            .string
        )["merchant"]["locations"]
        for _ in locations:
            addr = _["address"]
            street_address = f'{addr["floor_unit_no"]} { addr["building"]} {addr["street_no"]} {addr["street"]} {addr["corner_street"]} {addr["neighborhood"]}'
            temp = {}
            hours = []
            for hh in _["schedules"]:
                if hh["schedule_type"]["name"] == "Business Hours":
                    temp[
                        hh["day_type"]["name"]
                    ] = f"{hh['start_time']} - {hh['end_time']}"
            for day in days:
                hours.append(f"{day}: {temp[day]}")
            latitude = addr["latitude"]
            if latitude == 0.0:
                latitude = ""
            longitude = addr["longitude"]
            if longitude == 0.0:
                longitude = ""
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address.strip(),
                city=addr["city"],
                zip_postal=addr["zipcode"],
                latitude=latitude,
                longitude=longitude,
                country_code="PH",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
