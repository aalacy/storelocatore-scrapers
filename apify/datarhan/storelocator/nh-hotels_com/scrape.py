# -*- coding: utf-8 -*-
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

    start_url = "https://www.nh-hotels.com/hotels"
    domain = "nh-hotels.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_countries = dom.xpath("//h3/a/@href")
    for url in all_countries:
        response = session.get(url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[contains(@href, "/hotel/")]/@href')
        for l_url in all_locations:
            page_url = urljoin(start_url, l_url)
            loc_response = session.get(page_url, headers=hdr)
            store_number = re.findall(r"hotelTcm =  (.+?);", loc_response.text)[0]
            poi = session.get(
                f"https://www.nh-hotels.com/rest/datalayer/hotelPage/{store_number}",
                headers=hdr,
            ).json()
            street_address = poi["address"]["street"]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            zip_code = poi["address"]["postalCode"]
            if zip_code:
                zip_code = zip_code.split("Mey")[0].split("Flu")[0].split("San")[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state="",
                zip_postal=zip_code,
                country_code=poi["country"],
                store_number=store_number,
                phone=poi["contact"]["phone"],
                location_type="",
                latitude=poi["address"]["latitud"],
                longitude=poi["address"]["longitud"],
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
