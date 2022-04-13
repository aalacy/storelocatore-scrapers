from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "reddyice.com"
    start_url = "https://www.reddyice.com/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="location_link"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h5[@class="entry-title post-title"]/text()')[0]
        raw_address = loc_dom.xpath("//address/span/text()")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if "suit" in raw_address[1].lower():
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        if "suit" in raw_address[0].lower():
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        if "unit" in raw_address[0].lower():
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        geo = (
            loc_dom.xpath('//a[@class="google-map_link"]/@href')[0]
            .split("=")[-1]
            .split(",")
        )
        hoo = ""
        hoo_raw = loc_dom.xpath('//table[@id="ld-Responsive-table"]/tbody/tr/td')
        if hoo_raw:
            hoo = []
            for e in hoo_raw:
                day = e.xpath("@data-title")[0]
                hours = e.xpath("text()")
                hours = hours[0] if hours else ""
                hoo.append(f"{day}: {hours}")
            hoo = " ".join(hoo)
        store_number = str(loc_response.url).split("/")[-2].split("-")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[-1].split()[0],
            zip_postal=raw_address[-1].split()[-1],
            country_code="",
            store_number=store_number,
            phone="",
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
