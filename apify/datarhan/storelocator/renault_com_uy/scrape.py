# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://www.google.com/maps/d/embed?mid=12vHZyJeLXOJbgpIyYNn7PYxaZcL7dkAm"
    )
    domain = "renault.com.uy"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = response.text.split('pageData = "')[1].split('";</script>')[0]
    data = json.loads(data.replace("\\", ""))

    all_locations = data[1][6][1][12][0][13][0]
    all_locations += data[1][6][0][12][0][13][0]
    for poi in all_locations:
        location_name = poi[5][0][1][0]
        street_address = ""
        city = ""
        hoo = ""
        phone = ""
        if poi[5][1]:
            raw_data = poi[5][1][1][0]
            street_address = raw_data.split("nTeléfono")[0].split("Ubicación:t")[1]
            if street_address.endswith("."):
                street_address = street_address[:-1]
            city = raw_data.split("Localidad:t")[1].split("nDepartamento")[0]
            hoo = raw_data.split("Horario:t")[1].split("nWeb")[0].replace("mn ", "m ")
            phone = (
                raw_data.split("Teléfono:t")[1]
                .split("nLocalidad")[0]
                .split(" - ")[0]
                .split("/")[0]
            )

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.renault.com.uy/servicios/mapa-concesionarios.html",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="UY",
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi[1][0][0][0],
            longitude=poi[1][0][0][1],
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
