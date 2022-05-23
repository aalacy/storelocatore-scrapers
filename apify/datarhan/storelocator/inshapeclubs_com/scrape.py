# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "inshape.com"
    start_url = "https://www.inshape.com/DesktopModules/Inshape_Club/Api/ClubUI/GetClubList/?Language=en-US&moduleid=508&tabid=86&pageSize=999"

    data = session.get(start_url).json()
    for poi in data["data"]["items"]:
        hoo = etree.HTML(poi["ClubHours"]).xpath("//text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["ClubUrl"],
            location_name=poi["ClubName"],
            street_address=poi["ClubAddress"],
            city=poi["ClubCity"],
            state=poi["ClubState"],
            zip_postal=poi["ClubZip"],
            country_code="",
            store_number=poi["ClubId"],
            phone=poi["ClubPhone"],
            location_type="",
            latitude=poi["Coordinate"].split(",")[0],
            longitude=poi["Coordinate"].split(",")[-1],
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
