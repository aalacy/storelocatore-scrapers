# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.galeria.de/filialfinder"
    domain = "galeria.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//select[@name="dwfrm_storelocator_store"]/option/@value'
    )[1:]
    for store_number in all_locations:
        page_url = f"https://www.galeria.de/on/demandware.store/Sites-Galeria-Site/de/Stores-Details?StoreID={store_number}"
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@itemprop="name"]/text()')[0]
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[
            0
        ].strip()
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = loc_dom.xpath('//span[@itemprop="addressCountry"]/text()')[0]
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')[0]
        hoo = " ".join(
            loc_dom.xpath('//span[@itemprop="openingHours"]/text()')[0].split()
        )
        geo = (
            loc_dom.xpath('//img[contains(@src, "maps.googleapis")]/@src')[0]
            .split("7C")[-1]
            .split("&")[0]
            .split(",")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
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
