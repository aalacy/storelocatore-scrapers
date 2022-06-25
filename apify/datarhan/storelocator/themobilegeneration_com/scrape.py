from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://themobilegeneration.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMo5R0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABaMWvA"
    domain = "themobilegeneration.com"

    data = session.get(start_url).json()
    for poi in data["markers"]:
        raw_address = poi["address"].split(", ")
        raw_data = etree.HTML(poi["description"]).xpath("//text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        zip_code = raw_address[2].split()[-1]
        if len(zip_code) == 2:
            zip_code = ""
        page_url = f"https://themobilegeneration.com{poi['link']}"
        hoo = " ".join(raw_data[1:])
        phone = raw_data[0]
        if not zip_code:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_data = loc_dom.xpath('//p[@class="gbcols_p"]/text()')
            raw_data = [e.strip() for e in raw_data if e.strip() and e.strip() != "<"]
            zip_code = raw_data[1].split()[-1]
            hoo = " ".join([e for e in raw_data[1:] if " PM" in e])
            phone = raw_data[2]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"],
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[2].split()[0],
            zip_postal=zip_code,
            country_code=raw_address[3],
            store_number=poi["id"],
            phone=phone,
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
