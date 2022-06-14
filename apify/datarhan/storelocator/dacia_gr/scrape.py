# -*- coding: utf-8 -*-
import re
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = {
        "https://www.dacia.gr/dealerlocator.html": "https://dsi-dl.makolab.pl/service/dealers.svc/dealers/DACIA_GR?callback=jQuery1102049860075981215024_1655058031972&_=1655058031973",
        "https://www.dacia.ba/za-kupce/koncesionari.html": "https://dsi-dl.makolab.pl/service/dealers.svc/dealers/ba?callback=jQuery110205789675121154632_1655058243855&_=1655058243856",
        "https://www.dacia.ee/ee/dealerlocator.html": "https://dsi-dl.makolab.pl/service/dealers.svc/dealers/DACIA_EE?callback=jQuery1102044705256992955134_1655058279700&_=1655058279701",
        "https://www.dacia.lv/lv/dealerlocator.html": "https://dsi-dl.makolab.pl/service/dealers.svc/dealers/DACIA_LV?callback=jQuery11020861862962665902_1655058360663&_=1655058360664",
        "https://www.dacia.lt/dealerlocator.html": "https://dsi-dl.makolab.pl/service/dealers.svc/dealers/DACIA_LT?callback=jQuery110207269970262208378_1655058487198&_=1655058487199",
    }
    domain = "dacia.gr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    for page_url, start_url in start_urls.items():
        response = session.get(start_url, headers=hdr)
        data = re.findall(r"jQuery.+?\((.+?)\);", response.text)[0]

        all_locations = json.loads(data)
        for poi in all_locations:
            street_address = poi["AddressLine1"]
            if poi["AddressLine2"]:
                street_address += " " + poi["AddressLine2"]
            if poi["AddressLine3"]:
                street_address += " " + poi["AddressLine3"]
            services = poi["AvailableServices"]
            location_type = []
            types = {
                "17e1082f-ac48-4778-a6b0-38c128d683c2": "Bodyshop",
                "40582cfc-c083-4bab-80c4-302be907e67e": "Dacia prodaja",
                "28a188ec-614c-4ef0-83b0-b658c5a8e7f9": "Punjač za električna vozila",
                "f140bfe4-2926-421b-a7f7-b87a6c89cd10": "KASUTATUD AUTODE SPETSIALIST",
                "31987f0d-d13d-49fc-98bd-7dd675175e7c": "ELEKTRINIŲ AUTOMOBILIŲ AUTOSERVISAS",
                "3be1029e-e521-40f2-b22a-d26c9c893b08": "FINANSAVIMAS",
                "ee1e617d-740a-4e14-98a6-e594a9f706fc": "NAUDOTŲ KOMERCINIŲ AUTOMOBILIŲ VADYBININKAS",
                "f38f4b0f-7d3e-4322-a228-a79fb8a2227c": "AUTOSERVISAS",
                "e8821c46-86c7-41b1-9b8e-a27c5d388d71": "Sales",
                "ff6cdca6-b177-47b9-b730-878c3aa74e8a": "Repair",
            }
            for e in services:
                location_type.append(types[e])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["DealerName"],
                street_address=street_address,
                city=poi["City"],
                state="",
                zip_postal=poi["Postcode"],
                country_code=page_url.split("/")[2].split(".")[-1],
                store_number=poi["UniqueId"],
                phone=poi["Phone"].split(",")[0].split("i")[0],
                location_type=", ".join(location_type),
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
                hours_of_operation="",
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
