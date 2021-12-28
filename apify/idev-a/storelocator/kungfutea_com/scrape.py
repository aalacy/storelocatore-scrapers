from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kungfutea.com"
base_url = "https://www.kungfutea.com/locations/usa"
urls = {
    "US": "https://api.storepoint.co/v1/15dcedfc240d49/locations?rq",
    "AUS": "https://api.storepoint.co/v1/1594ac508c7d24/locations?rq",
}


def fetch_data():
    with SgRequests() as session:
        for country, json_url in urls.items():
            locations = session.get(json_url, headers=_headers).json()["results"][
                "locations"
            ]
            for _ in locations:
                if "coming soon" in _["name"].lower():
                    continue

                addr = parse_address_intl(_["streetaddress"])
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if _["monday"] == "":
                    hours_of_operation = "<MISSING>"
                else:
                    hours_of_operation = (
                        "Monday: "
                        + _["monday"]
                        + ", "
                        + "Tuesday: "
                        + _["tuesday"]
                        + ", "
                        + "Wednesday: "
                        + _["wednesday"]
                        + ", "
                        + "Thursday: "
                        + _["thursday"]
                        + ", "
                        + "Friday: "
                        + _["friday"]
                        + ", "
                        + "Saturday: "
                        + _["saturday"]
                        + ", "
                        + "Sunday: "
                        + _["sunday"]
                    )

                location_type = ""
                if "temporarily closed" in _["name"].lower():
                    location_type = "temporarily closed"
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=country,
                    phone=_["phone"],
                    location_type=location_type,
                    locator_domain=locator_domain,
                    latitude=_["loc_lat"],
                    longitude=_["loc_long"],
                    hours_of_operation=hours_of_operation.replace(",", ";").replace(
                        "–", "-"
                    ),
                    raw_address=_["streetaddress"],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
