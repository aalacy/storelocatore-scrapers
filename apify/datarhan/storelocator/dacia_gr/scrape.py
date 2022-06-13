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
                location_type="",
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
