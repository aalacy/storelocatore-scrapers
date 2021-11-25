from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "haggar.com"
    start_url = "https://www.haggar.com/storelisting"

    response = session.get("https://www.haggar.com/stores/?lang=default")
    dom = etree.HTML(response.text)
    formdata = {
        "dwfrm_storelocator_countryCode": "US",
        "dwfrm_storelocator_distanceUnit": "mi",
        "dwfrm_storelocator_postalCode": "10001",
        "dwfrm_storelocator_maxdistance": "999999",
        "dwfrm_storelocator_findbyzip": "Search",
    }
    response = session.post(start_url, data=formdata)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//table[@id="store-location-results"]/tbody/tr')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@class="store-details-link"]/@href')
        store_url = "https://www.haggar.com" + store_url[0] if store_url else ""
        location_name = poi_html.xpath('.//div[@class="store-name"]/span/text()')
        location_name = location_name[0].strip() if location_name else ""
        raw_address = poi_html.xpath('.//td[@class="store-address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) == 4:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = ""
        city = ""
        state = ""
        zip_code = ""
        country_code = ""
        if raw_address:
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = raw_address[-1]
        phone = poi_html.xpath('.//a[@class="phone-number"]/text()')
        phone = phone[0] if phone else ""
        hoo = poi_html.xpath('//div[@class="store-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = (
            " ".join(hoo).split("Thanksgiving")[0].strip() if hoo else ""
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hours_of_operation,
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
