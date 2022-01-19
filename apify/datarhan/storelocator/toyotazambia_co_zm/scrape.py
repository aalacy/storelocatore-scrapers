import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotazambia.co.zm/dealers/"
    domain = "toyotazambia.co.zm"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="media-box post-image"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        store_number = page_url.split("=")[-1]
        url = f"https://www.toyotazambia.co.zm/Umbraco/Api/Dealers/GetDealer?dealerId={store_number}"
        poi = session.get(url).json()
        hoo = poi["WorkingTime"]
        if hoo == "n/a":
            hoo = ""
        geo = ["", ""]
        geo_data = re.findall(r"LatLng\((.+?)\);", loc_response.text)
        if geo_data:
            geo = geo_data[0].split(", ")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Name"],
            street_address=poi["Address"],
            city=poi["City"],
            state="",
            zip_postal="",
            country_code="ZM",
            store_number=store_number,
            phone=poi["Phone"].split("/")[0].strip(),
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
