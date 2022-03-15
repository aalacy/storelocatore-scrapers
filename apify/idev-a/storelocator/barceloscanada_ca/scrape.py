from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://barceloscanada.ca/"
    page_url = "https://barceloscanada.ca/locations/"
    base_url = "https://barceloscanada.ca/wp-admin/admin-ajax.php?action=restaurant_listings_locate_restaurant&origLat=37.09024&origLng=-95.712891"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = parse_address_intl(_["properties"]["address"])
            yield SgRecord(
                page_url=page_url,
                location_name=_["properties"]["name"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                latitude=_["geometry"]["coordinates"][1],
                longitude=_["geometry"]["coordinates"][0],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
