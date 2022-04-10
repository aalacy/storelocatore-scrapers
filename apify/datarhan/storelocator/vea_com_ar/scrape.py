# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.vea.com.ar/api/dataentities/NT/search?_fields=name,grouping,image_maps,geocoordinates,SellerName,id,country,city,neighborhood,number,postalCode,state,street,schedule,services,paymentMethods,opening,hasPickup,hasDelivery,address,url_image,phone,%20&_where=isActive=true&_sort=name%20ASC"
    domain = "vea.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "REST-Range": "resources=0-999",
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        geo = poi["geocoordinates"].split(",")

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.vea.com.ar/sucursales",
            location_name=poi["name"],
            street_address=poi["address"].split(" - ")[0].replace("Sin info", ""),
            city=poi["grouping"],
            state=poi["state"],
            zip_postal=poi["postalCode"],
            country_code=poi["country"],
            store_number="",
            phone=poi["phone"],
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=poi["schedule"]
            .replace("Atención: ", "")
            .split("Horarios")[0]
            .replace("Sin info", "")
            .strip(),
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
