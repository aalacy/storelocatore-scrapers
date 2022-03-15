import re
import demjson
from lxml import etree
from time import sleep
from random import uniform

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "millersalehouse.com"
    start_url = "https://millersalehouse.com/locations/"
    hdr = {
        "X-Requested-With": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    response = session.post(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "var locations")]/text()')[0]
    all_locations = re.findall(
        "var locations = (.+);", data.replace("\n", "").replace("\t", "")
    )[0]
    all_locations = re.sub(r"new google.maps.LatLng\((.+?)\),", '"\1",', all_locations)
    all_locations = demjson.decode(all_locations)
    for poi in all_locations:
        if "Coming Soon" in poi["name"]:
            continue
        poi_html = etree.HTML(poi["content"])
        raw_address = poi_html.xpath('//span[@class="address"]/text()')
        sleep(uniform(3, 10))

        hdr = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        loc_response = session.get(poi["url"], headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath(
            '//span[contains(text(), "Hours")]/following-sibling::fieldset//text()'
        )
        hoo = (
            " ".join([e.strip() for e in hoo if e.strip()])
            .split("*")[0]
            .split("We are open!")[0]
            .strip()
        )
        location_name = (
            poi["name"].replace("&#8217", "'").replace("&#8211; Now Open!", "")
        )
        street_address = (
            poi["street"].replace("<br>", " ").replace(" Crossings Plaza", "")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["url"],
            location_name=location_name,
            street_address=street_address,
            city=raw_address[-1].split(", ")[0],
            state=raw_address[-1].split(", ")[-1].split()[0],
            zip_postal=poi["zip"],
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["coords"].split(",")[0],
            longitude=poi["coords"].split(",")[-1],
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
