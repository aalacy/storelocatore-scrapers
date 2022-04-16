# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.atacadao.com.br/lojas/stores-query?uf=null"
    domain = "atacadao.com.br"

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        page_url = urljoin("https://www.atacadao.com.br/lojas/", poi["slug"])
        hoo = f'Segunda a Sábado: {poi["working_days_start"][:-3]} às {poi["working_days_end"][:-3]}, Domingos: {poi["sunday_start"][:-3]} às {poi["sunday_end"][:-3]}'

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=f"{poi['address_street']}, {poi['address_number']}",
            city=poi["address_city"],
            state=poi["address_state"],
            zip_postal=poi["address_cep"],
            country_code="BR",
            store_number=poi["pk"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
