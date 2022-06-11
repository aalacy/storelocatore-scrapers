import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "accor.com"
    start_urls = [
        "https://all.accor.com/ssr/app/ibis/hotels/united-kingdom/index.en.shtml",
        "https://all.accor.com/ssr/app/ibis/hotels/united-states/index.en.shtml",
        "https://all.accor.com/ssr/app/ibis/hotels/canada/index.en.shtml",
    ]

    for start_url in start_urls:
        response = session.get(start_url)
        all_ids = re.findall('id:"(.+?)",name', response.text)
        for loc_id in all_ids:
            page_url = f"https://all.accor.com/hotel/{loc_id}/index.en.shtml?dateIn=&nights=&compositions=&stayplus=false#origin=ibis"
            loc_response = session.get(page_url)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath(
                '//script[@type="application/ld+json" and contains(text(), "telephone")]/text()'
            )
            if not poi:
                continue
            poi = json.loads(poi[0])
            add_data = loc_dom.xpath('//script[contains(text(), "hotelName")]/text()')[
                0
            ]
            add_data = json.loads(add_data)
            latitude = loc_dom.xpath('//meta[@property="og:latitude"]/@content')
            latitude = latitude[0] if latitude else ""
            longitude = loc_dom.xpath('//meta[@property="og:longitude"]/@content')
            longitude = longitude[0] if longitude else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=add_data["streetAddress"],
                city=poi["address"]["addressLocality"],
                state="",
                zip_postal=poi["address"]["postalCode"],
                country_code=poi["address"]["addressCountry"],
                store_number=loc_id,
                phone=poi["telephone"],
                location_type=poi["@type"],
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
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
