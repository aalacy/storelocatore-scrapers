import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "http://www.cinnabonkw.com/locate"
    domain = "cinnabonkw.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "gMap")]/text()')[0]
    data = re.findall(r"Maplace\((.+?)\).Load", data.replace("\n", ""))[0]
    data = data.replace(
        '// {        // title: "<strong>Test Store <br> <small></small> <br> <small>Timings : 24Hours</small> <br> <small>Phone Number : 1849090</small>"  ,        // html: \'<strong>Cinnabon - Seattles Best Coffee (Waha Mall)</strong><p></p><ul class="locate_ul"><li><i class="fa fa-fw fa-map-marker"></i>Jassem Mohammad Al-Kharafi Rd., Dhajeej</li><li><i class="fa fa-fw fa-phone"></i>1849090</li><li><i class="fa fa-fw fa-envelope-o"></i>mai@cinnabon.com</li><li><i class="fa fa-fw fa-clock-o"></i>THU-SAT : 24Hours</li></ul>\',        // lat: ,        // lon: ,        // zoom: 14        // },',
        "",
    )
    data = demjson.decode(data)

    for poi in data["locations"]:
        poi_html = etree.HTML(poi["html"])
        location_name = poi_html.xpath("//strong/text()")[0]
        raw_data = poi_html.xpath("//li/text()")
        addr = parse_address_intl(raw_data[0])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=raw_data[1],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lon"],
            hours_of_operation=raw_data[-1],
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
