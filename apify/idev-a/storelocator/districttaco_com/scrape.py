from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.districttaco.com/"
    page_url = "https://www.districttaco.com/pages/locations"
    base_url = "https://crafty-cairn-164919.ue.r.appspot.com/website/getYextLocations"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = parse_address_intl(f"{_['addressline1']} {_['addressline2']}")
            hours = [f"Monday: {_['Monday']}"]
            hours.append(f"Tuesday: {_['Tuesday']}")
            hours.append(f"Wednesday: {_['Wednesday']}")
            hours.append(f"Thursday: {_['Thursday']}")
            hours.append(f"Friday: {_['Friday']}")
            hours.append(f"Saturday: {_['Saturday']}")
            hours.append(f"Sunday: {_['Sunday']}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["storeName"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["phone"],
                location_type=_["type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
