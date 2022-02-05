from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://fattuesday.com"
base_url = "https://fattuesday.com/locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("section.locations-map")["x-data"]
            .replace("locations(", "")[:-1]
        )["locations"]
        for _ in locations:
            if (
                "coming soon" in _["hours"].lower()
                or "coming 2022" in _["hours"].lower()
                or "coming winter" in _["hours"].lower()
            ):
                continue

            hours = []
            for hh in bs(_["hours"], "lxml").stripped_strings:
                if "Hour" in hh or "Please" in hh:
                    break
                hours.append(hh)
            if "coming" in _["hours"].lower():
                hours = []

            addr = parse_address_intl(_["address"])
            if "United States" in _["address"]:
                addr = _["address"].split(",")
                street_address = ", ".join(addr[:-2])
                city = ""
                if "Las Vegas" in street_address:
                    street_address = street_address.replace("Las Vegas", "").strip()
                    if street_address.endswith(","):
                        street_address = street_address[:-1]
                    city = "Las Vegas"

                state = addr[-2].strip().split()[0]
                zip_postal = addr[-2].strip().split()[-1]
                country_code = "United States"
            else:
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
                country_code = addr.country
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
