import json
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "chatime-usa.com"
    start_url = "https://chatime-usa.com/wp-admin/admin-ajax.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    formdata = {
        "action": "lsajax_search_results",
        "lat": "40.75368539999999",
        "lng": "-73.9991637",
        "distance": "50000",
        "distance_units": "km",
        "query_type": "postcode",
        "query_values[]": "10001",
        "query_values[]": "10001",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        poi_html = etree.HTML(poi["resultsItemHTML"])
        page_url = "https://chatime-usa.com/locations/"
        location_name = poi_html.xpath(".//h3/text()")
        location_name = location_name[0] if location_name else ""
        raw_address = poi_html.xpath(".//address//text()")
        raw_address = [
            e.strip() for e in raw_address if e.strip() and "get " not in e.lower()
        ]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if not street_address:
            street_address = addr.street_address_2
        if not street_address:
            street_address = raw_address.split(",")[0]
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        store_number = poi["i"]
        phone = poi_html.xpath('.//p[@class="lsform__result__details"]/text()')
        phone = phone[0] if phone else ""
        latitude = poi["lat"]
        longitude = poi["lng"]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
