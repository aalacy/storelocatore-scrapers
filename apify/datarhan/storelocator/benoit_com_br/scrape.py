# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.benoit.com.br/onde-encontrar"
    domain = "benoit.com.br"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "wdPointOfSales")]/text()')[0]
        .split("wdPointOfSales = ")[-1]
        .strip()[:-1]
    )
    all_locations = json.loads(data)
    for poi in all_locations:
        phone = ""
        hoo = ""
        if poi["Description"]:
            phone = poi["Description"].split("|")[-1]
            phone = phone.split(":")[-1] if phone and "Telefone" in phone else ""
            hoo = poi["Description"].split("|")[0].split("de Atendimento:")[-1]
            if "Telefone" in hoo:
                hoo = ""
        street_address = f"{poi['AddressLine']} {poi['AddressNumber']}"
        latitude = poi["Latitude"]
        latitude = latitude if latitude and latitude != "0.0" else ""
        longitude = poi["Longitude"]
        longitude = longitude if longitude and longitude != "0.0" else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.benoit.com.br/onde-encontrar",
            location_name=poi["Name"],
            street_address=street_address,
            city=poi["City"],
            state=poi["State"],
            zip_postal=poi["PostalCode"],
            country_code="BR",
            store_number=poi["PointOfSaleID"],
            phone=poi["Phone"],
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
