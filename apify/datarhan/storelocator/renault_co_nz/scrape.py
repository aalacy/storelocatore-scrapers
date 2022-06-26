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

    start_url = "https://www.renault.co.nz/renault-dealership-service-centre"
    domain = "renault.co.nz"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(
        "https://www.renault.co.nz/renault/locations", headers=hdr
    ).json()
    for r in data["Regions"]:
        for poi in r["Dealers"]:
            raw_address = poi["Address"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hoo = ""
            if poi["WorkingHours"]:
                hoo = " ".join(
                    " ".join(etree.HTML(poi["WorkingHours"]).xpath("//text()")).split()
                )
                if "Service" in hoo:
                    hoo = hoo.split("Service")[0].split("Sales")[1].strip()
                hoo = hoo.split("Hours:")[-1]
                if hoo.startswith(":"):
                    hoo = hoo[1:]

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["Name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="NZ",
                store_number=poi["BranchId"],
                phone=poi["Phone"],
                location_type=", ".join(poi["Type"]),
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
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
