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

    start_url = "https://briochedoree.us/our-locations/"
    domain = "briochedoree.us"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    data = (
        dom.xpath('//script[contains(text(), "arrLocation")]/text()')[0]
        .split("arrLocation =")[-1]
        .strip()[:-1]
    )
    all_locations = json.loads(data)
    for poi in all_locations:
        mon = f'MONDAY {poi["heureLundiDebut"]} - {poi["heureLundiFin"]}'
        tue = f'TUESDAY {poi["heureMardiDebut"]} - {poi["heureMardiFin"]}'
        wed = f'WEDNESDAY {poi["heureMercrediDebut"]} - {poi["heureMercrediFin"]}'
        thu = f'THURSDAY {poi["heureJeudiDebut"]} - {poi["heureJeudiFin"]}'
        fri = f'FRIDAY {poi["heureVendrediDebut"]} - {poi["heureVendrediFin"]}'
        sat = f'SATURDAY {poi["heureSamediDebut"]} - {poi["heureSamediFin"]}'
        sun = f'SUNDAY {poi["heureDimancheDebut"]} - {poi["heureDimancheFin"]}'
        hoo = f"{mon}, {tue}, {wed}, {thu}, {fri}, {sat}, {sun}".replace(
            "Closed - Closed", "Closed"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["url"],
            location_name=poi["titre"],
            street_address=poi["rue"] + ", " + poi["infoSup"],
            city=poi["ville"].split(", ")[0],
            state=poi["ville"].split(", ")[-1],
            zip_postal=poi["codepostal"],
            country_code="",
            store_number=poi["id"],
            phone=poi["managerTel"],
            location_type=poi["typelocation"],
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
