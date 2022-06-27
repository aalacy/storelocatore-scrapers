from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

header1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.wellstar.org",
    "referer": "https://www.wellstar.org/locations",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
locator_domain = "https://www.wellstar.org"
base_url = "https://www.wellstar.org/locations"
json_url = "https://www.wellstar.org/api/LocationSearchApi/GetLocations"


def fetch_data():
    with SgRequests() as session:
        sp1 = bs(session.get(base_url, headers=header1).text, "lxml")
        _headers["__requestverificationtoken"] = sp1.select_one(
            'input[name="__RequestVerificationToken"]'
        )["value"]
        data = {
            "searchTerm": "",
            "filters": "",
            "locationId": "ChIJ5SwYpkkV9YgRP7wgDLyCZX8",
            "distance": "any",
            "locationCurrent": "false",
            "location": "",
        }
        locations = session.post(json_url, headers=_headers, json=data).json()[
            "matchingItems"
        ]
        for _ in locations:
            page_url = locator_domain + _["PageURL"]
            raw_address = _["Address"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if _["Address2"]:
                street_address += " " + _["Address2"]
            hours = []
            if _.get("Hours"):
                for day in days:
                    hours.append(f"{day}: {_['Hours'].get(day)}")
            if _["Open24Hours"]:
                hours = ["Open 24 hours"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["Name"],
                store_number=_["LocationID"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="US",
                phone=_["LocationContactPhone"],
                locator_domain=locator_domain,
                location_type=", ".join(_["LocationTypes"]),
                hours_of_operation="; ".join(hours),
                raw_address=_["Address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
