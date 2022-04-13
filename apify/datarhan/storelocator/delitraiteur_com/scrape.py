# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://delitraiteur.com/wp-admin/admin-ajax.php?lang=fr&action=store_search&lat=50.85034&lng=4.35171&max_results=100&search_radius=200&autoload=1"
    domain = "delitraiteur.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        hoo = etree.HTML(poi["hours"]).xpath("//text()")
        hoo = " ".join(hoo)
        page_url = poi["permalink"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath(
            '//div[div[h2[contains(text(), "Téléphone")]]]/following-sibling::div[1]//p/text()'
        )[0]
        location_name = loc_dom.xpath("//h1/text()")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
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
