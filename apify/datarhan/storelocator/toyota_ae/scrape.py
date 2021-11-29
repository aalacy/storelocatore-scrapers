import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.ae/en/our-locations/"
    domain = "toyota.ae"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
    data = json.loads(data)
    all_locations = data["props"]["pageProps"]["locationLists"]["locationList"]
    for poi in all_locations:
        page_url = f"https://www.toyota.ae/en/our-locations/{poi['name']}/"
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/@href')[0].split(":")[-1]
        hoo = f"{poi['Opening_Time']} - {poi['Closing_Time']}"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Location_Name"],
            street_address=poi["Address"],
            city=poi["emirates"],
            state=poi["emirates_code"],
            zip_postal="",
            country_code="AE",
            store_number="",
            phone=phone,
            location_type=poi["LocationType"],
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
