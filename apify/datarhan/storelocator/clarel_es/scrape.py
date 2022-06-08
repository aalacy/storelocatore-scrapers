from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "clarel.es"

    hdr = {
        "accept": "*/*",
        "content-type": "application/json",
        "Referer": "",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    }
    frm = {
        "operationName": "getStoresList",
        "query": "query getStoresList($lat: Float!, $lng: Float!, $searchRadiusKm: Int, $limit: Int) {\n  storesList(lat: $lat, lng: $lng, searchRadiusKm: $searchRadiusKm, limit: $limit) {\n    ...StoreLocatorAttributes\n  }\n}\n\nfragment StoreLocatorAttributes on StoreLocator {\n  __typename\n  id\n  code\n  name\n  address1: address_1\n  address2: address_2\n  city\n  state\n  zip\n  countryId: country_id\n  country\n  phone\n  lat\n  lng\n  opening\n  enable\n  distance\n  pickupStore: pickup_store\n}\n",
        "variables": {"lat": 40.4378698, "lng": -3.8196207},
    }
    data = session.post("https://www.clarel.es/graphql", json=frm, headers=hdr).json()

    for poi in data["data"]["storesList"]:

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.clarel.es/es/encuentra-tu-tienda",
            location_name=poi["name"],
            street_address=poi["address1"],
            city=poi["city"],
            state="",
            zip_postal=poi["zip"],
            country_code=poi["countryId"],
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation="",
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
