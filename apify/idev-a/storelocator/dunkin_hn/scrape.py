from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkin.hn"
base_url = "https://www.com1dav1rtual.com/api/em/store/get_filter"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        payload = {"business_partner": "4"}
        locations = session.post(base_url, headers=_headers, json=payload).json()
        for _ in locations:
            street_address = (
                _["address"]
                .replace(_["location_two_name"], "")
                .replace(_["location_one_name"], "")
                .strip()
            )
            hours = []
            for hh in _.get("general_range_hour", []):
                hr = hh["name"].split()
                if hh["name"] == "null null":
                    times = "De 12:00 AM a 12:00 AM"
                else:
                    times = f"De {hr[0]} AM a {hr[1]} PM"
                hours.append(times)
            yield SgRecord(
                page_url="https://dunkin.hn/informacion-restaurantes",
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["location_two_name"],
                state=_["location_one_name"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country_name"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
