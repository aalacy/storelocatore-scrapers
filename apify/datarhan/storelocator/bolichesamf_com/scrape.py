from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://bolichesamf.com/sucursales-boliches-amf/"
    domain = "bolichesamf.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="branch-card text-center"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h4/text()")[0]
        raw_address = [
            e.strip() for e in poi_html.xpath(".//p/text()") if "Tels" not in e
        ]
        phone = poi_html.xpath(".//p/text()")[-1].split(":")[-1]
        geo = (
            poi_html.xpath('.//a[contains(@href, "waze")]/@href')[0]
            .split("=")[1]
            .split("&")[0]
            .split(",")
        )
        hoo = poi_html.xpath(
            './/following-sibling::div[1]//p[contains(@id, "schedule")]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        hoo = " ".join(hoo.split())
        zip_code = raw_address[-1].split()[-2]
        city = " ".join(raw_address[-1].split()[:-2])
        if not zip_code.isdigit():
            city = zip_code = raw_address[-1].split(",")[0].replace("N.L.", "").strip()
            zip_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=", ".join(raw_address[:-1])[:-1],
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="MX",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
