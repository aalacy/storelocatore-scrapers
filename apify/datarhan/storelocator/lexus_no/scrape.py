import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.no/local-retailer/choose-a-dealer/"
    domain = "lexus.no"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="dealer-details"]')
    for poi_html in all_locations:
        url = poi_html.xpath(".//a[@data-gt-dealername]/@href")[-1]
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[contains(text(), "address")]/text()')
        hoo = ""
        if data:
            poi = json.loads(data[0])
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            zip_code = poi["address"]["postalCode"]
            phone = poi["telephone"]
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = loc_dom.xpath(
                '//h3[label[contains(text(), "Showroom")]]/following-sibling::ul[1]//text()'
            )
            hoo = [e.replace("&nbsp", "").strip() for e in hoo if e.strip()]
            hoo = (
                " ".join(hoo).split("   Åpningstider")[0].replace("I dag: ", "").strip()
            )
            if hoo == "Åpningstider Mandag  Tirsdag  Onsdag  Torsdag  Fredag  lørdag":
                hoo = ""
        else:
            location_name = poi_html.xpath(".//h2/text()")[0]
            raw_address = poi_html.xpath('.//li[@class="address"]/text()')[0].strip()
            street_address = raw_address.split("-")[0]
            city = raw_address.split("-")[1]
            zip_code = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="NO",
            store_number="",
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
