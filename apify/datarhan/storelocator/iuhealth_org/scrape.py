import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "iuhealth.org"
    start_url = "https://4ihkkbfuuk-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.3.1)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.2.1)%3B%20react%20(16.8.6)%3B%20react-instantsearch%20(6.7.0)&x-algolia-api-key=cc321cac4dc07696439db06c6a06144b&x-algolia-application-id=4IHKKBFUUK"
    body = '{"requests":[{"indexName":"locations","params":"highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&maxValuesPerFacet=5000&query=&hitsPerPage=1200&getRankingInfo=true&aroundLatLng=&aroundRadius=all&filters=type%3Alocation%20OR%20type%3Ahospital&clickAnalytics=true&analyticsTags=findLocationPage&page=0&facets=%5B%22address.city%22%2C%22facilityType%22%2C%22umbrellaServices%22%5D&tagFilters="}]}'
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["results"][0]["hits"]:
        store_url = "https://iuhealth.org/find-locations/" + poi["slug"]
        location_name = poi["name"]
        street_address = poi["address"]["address1"]
        if poi["address"]["address2"]:
            street_address += " " + poi["address"]["address2"]
        city = poi["address"]["city"]
        state = poi["address"]["state"]
        zip_code = poi["address"]["zip"]
        store_number = poi["entryID"]
        phone = poi["phone"]
        location_type = poi["facilityType"]
        latitude = poi["_geoloc"]["lat"]
        longitude = poi["_geoloc"]["lng"]

        h_response = session.get(
            f"https://iuhealth.org/find-locations/hours?id={store_number}"
        )
        hoo = ""
        if h_response.status_code == 200:
            h_dom = etree.HTML(h_response.text)
            if h_dom:
                hoo = h_dom.xpath("//table//text()")
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
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
