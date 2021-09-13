import re
import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.sephora.ro/magazine.html"
    domain = "sephora.ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "var stores")]/text()')[0]
    data = re.findall("var stores = (.+?);\r\n", data)[0]

    all_locations = demjson.decode(data)
    for poi in all_locations:
        page_url = urljoin(start_url, poi["url"])
        city = poi["city"]
        city = city if "Sector" not in city else poi["cityname"]
        if "Sector" in city:
            city = "Bucuresti"
        phone = poi["phone1"]
        if not phone:
            phone = poi["phone2"]
        if not phone:
            phone = poi["phone3"]
        phone = phone.split("(<")[0].strip()
        hoo = []
        days = ["luni", "marti", "miercuri", "joi", "vineri", "sambata", "duminica"]
        for day in days:
            hoo.append(f"{day} {poi[day]}")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=city,
            state=SgRecord.MISSING,
            zip_postal=poi["zipcode"],
            country_code="RO",
            store_number=poi["storeid"],
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=" ".join(hoo),
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
