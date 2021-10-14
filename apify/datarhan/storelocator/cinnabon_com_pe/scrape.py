from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.cinnabon.com.pe/locales"
    domain = "cinnabon.com.pe"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "operationName": "getWebsitePage_cached",
        "variables": {"pageId": "utFXWzLWJhfFEEvT5", "websiteId": "229mN7d8DDtuSbvTd"},
        "query": "query getWebsitePage_cached($pageId: ID, $websiteId: ID) {\n  page(pageId: $pageId, websiteId: $websiteId) {\n    _id\n    path\n    activeComponents {\n      _id\n      options\n      componentTypeId\n      schedule {\n        isScheduled\n        latestScheduleStatus\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
    }
    data = session.post(
        "https://api.getjusto.com/graphql?operationName=getWebsitePage_cached",
        headers=hdr,
        json=frm,
    ).json()

    all_locations = data["data"]["page"]["activeComponents"][1]["options"]["stores"]
    for poi in all_locations:
        frm = {
            "operationName": "getPlaceDetails_cached",
            "variables": {"placeId": poi["placeId"]},
            "query": "query getPlaceDetails_cached($placeId: ID) {\n  place(placeId: $placeId) {\n    _id\n    text\n    secondaryText\n    location\n    __typename\n  }\n}\n",
        }
        poi_data = session.post(
            "https://api.getjusto.com/graphql?operationName=getPlaceDetails_cached",
            json=frm,
            headers=hdr,
        ).json()
        raw_data = poi_data["data"]["place"]["secondaryText"]
        addr = parse_address_intl(raw_data)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=poi_data["data"]["place"]["text"],
            city=addr.city,
            state=addr.state,
            zip_postal="",
            country_code="PE",
            store_number="",
            phone=poi["phone"],
            location_type="",
            latitude=poi_data["data"]["place"]["location"]["lat"],
            longitude=poi_data["data"]["place"]["location"]["lng"],
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
