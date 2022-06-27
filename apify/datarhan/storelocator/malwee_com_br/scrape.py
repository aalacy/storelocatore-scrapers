# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.malwee.com.br/api/dataentities/SL/search/?_fields=brand%2Ccity%2Ccomplement%2Cexpedient_week%2Cexpedient_weekend%2CID%2Clatitude%2Clongitude%2Cname%2Cneighborhood%2Cnumber%2Cobservation%2Cshopping_name%2Cstate%2Cstore_type%2Cstreet%2Czipcode%2Cid"
    domain = "malwee.com.br"
    hdr = {
        "accept": "application/vnd.vtex.ds.v10+json",
        "rest-range": "resources=0-500",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        street_address = f"{poi['street']}, {poi['number']}"
        weekend = poi["expedient_weekend"]
        if weekend == "0":
            weekend = "Fechado"
        hoo = f"Segunda à sexta - {poi['expedient_week']}, Sábado e domingo - {weekend}"
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.malwee.com.br/institucional/nossas-lojas",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zipcode"],
            country_code="",
            store_number=poi["ID"],
            phone="",
            location_type=poi["store_type"],
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
