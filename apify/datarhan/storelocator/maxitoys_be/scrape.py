# -*- coding: utf-8 -*-
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.maxitoys.be/magasins"
    domain = "maxitoys.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//input[@id="hdn_e_magasins"]/@value')[0]

    all_locations = json.loads(data)
    for poi in all_locations:
        page_url = urljoin(start_url, poi["Url"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        hoo = loc_dom.xpath(
            '//b[contains(text(), "Horaires")]/following-sibling::ol[1]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo[2:])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Libelle"],
            street_address=poi["Adresse"],
            city=poi["Ville"],
            state="",
            zip_postal=poi["CodePostal"],
            country_code=poi["Pays"],
            store_number=poi["Code"],
            phone=poi["Telephone"],
            location_type="",
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
