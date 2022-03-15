import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://miniso-ca.com/apps/store-locator/"
    domain = "miniso.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@id="addresses_list"]/ul/li')
    all_coords = re.findall(r"markersCoords.push\((.+?)\);", response.text)[:-2]
    all_coords = [demjson.decode(e) for e in all_coords]

    for poi_html in all_locations:
        location_name = poi_html.xpath('.//span[@class="name"]/text()')[0].strip()
        street_address = poi_html.xpath('.//span[@class="address"]/text()')[0].strip()
        city = poi_html.xpath('.//span[@class="city"]/text()')[0]
        state = poi_html.xpath('.//span[@class="prov_state"]/text()')[0]
        zip_code = poi_html.xpath('.//span[@class="postal_zip"]/text()')[0]
        country_code = poi_html.xpath('.//span[@class="country"]/text()')[0]
        hoo = poi_html.xpath('.//span[@class="hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        store_number = poi_html.xpath("@onmouseover")[0].split("(")[-1][:-1]
        geo = [e for e in all_coords if store_number == str(e["id"])][0]
        location_type = ""
        if "TEMPORARILY CLOSED" in hoo:
            location_type = "TEMPORARILY CLOSED"
            hoo = hoo.replace("TEMPORARILY CLOSED", "")

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone="",
            location_type=location_type,
            latitude=geo["lat"],
            longitude=geo["lng"],
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
