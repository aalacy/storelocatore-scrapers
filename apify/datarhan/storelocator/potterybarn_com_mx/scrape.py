# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://www.potterybarn.com.mx/tienda/browse/getListOfStates?stateListType=EDD"
    )
    domain = "potterybarn.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for state in data["estados"].values():
        url = f'https://www.potterybarn.com.mx/getnearbystoresByQueryPram?storeOrCityOrStateName={state["stateName"].replace(" ", "%20")}'
        s_data = session.get(url).json()

        all_locations = s_data["StoresList"]["data"]
        for poi in all_locations:
            poi_html = etree.HTML(poi["address"]["generalDetails"])
            raw_data = poi_html.xpath("//text()")
            raw_data = [e.strip() for e in raw_data if e.strip()]
            raw_address = raw_data[0].replace("\n", " ")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address.startswith("#"):
                street_address = street_address[1:]
            city = poi["address"]["deligationOrCity"]
            if city:
                city = city.split(",")[0]
            hoo = [e.split("tienda:")[-1].strip() for e in raw_data if "Horario" in e]
            hoo = hoo[0].split("Horario:")[-1].split("Tienda:")[-1] if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.potterybarn.com.mx/tienda/home",
                location_name=poi["storeName"],
                street_address=street_address,
                city=poi["address"]["deligationOrCity"],
                state=poi["address"]["state"],
                zip_postal=poi["address"]["zipCode"],
                country_code="MX",
                store_number=poi["storeId"],
                phone=poi["address"]["phoneNumber"],
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=hoo,
                raw_address=raw_address,
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
