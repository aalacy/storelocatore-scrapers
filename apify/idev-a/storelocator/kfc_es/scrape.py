from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kfc.es"
base_url = "https://api.kfc.es/configurations"


def fetch_data():
    with SgRequests() as session:
        for key in session.get(base_url, headers=_headers).json()["storeKeys"]:
            url = f"https://api.kfc.es/find-a-kfc/{key}"
            locations = session.get(url, headers=_headers).json()["Value"]
            logger.info(f"[{key}] {len(locations)} found")
            for store in locations:
                _ = store["googleBusinessData"]
                addr = parse_address_intl(_["address"])
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                page_url = f"https://www.kfc.es/encuentra-tu-kfc/{store['primaryAttributes']['slug']}"
                hours = []
                hours.append(f"Mon: {_['mondayHours']}")
                hours.append(f"Tue: {_['tuesdayHours']}")
                hours.append(f"Wed: {_['wednesdayHours']}")
                hours.append(f"Thu: {_['thursdayHours']}")
                hours.append(f"Fri: {_['fridayHours']}")
                hours.append(f"Sat: {_['saturdayHours']}")
                hours.append(f"Sun: {_['sundayHours']}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=store["primaryAttributes"]["id"],
                    location_name=store["primaryAttributes"]["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="Spain",
                    phone=_["telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=_["address"],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
