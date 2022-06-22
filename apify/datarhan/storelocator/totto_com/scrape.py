# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import demjson

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://redisenotottomx.vteximg.com.br/arquivos/allStoresData.js?v=637498064308830000"
    domain = "totto.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = response.text.split("allStoresData = ")[-1].strip()[:-1]
    all_countries = demjson.decode(
        data.replace("\r", "").replace("\n", "").replace("\t", "")
    )
    for country_code, data in all_countries.items():
        for city, locations in data["cities"].items():
            for location_name, poi in locations["stores"].items():
                phone = poi["phone"]
                if phone:
                    phone = phone.split("fax")[0]
                item = SgRecord(
                    locator_domain=domain,
                    page_url="https://mx.totto.com/tiendas",
                    location_name=location_name,
                    street_address=poi["address"],
                    city=city,
                    state="",
                    zip_postal="",
                    country_code=country_code,
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude=poi["lat"],
                    longitude=poi["lng"],
                    hours_of_operation=poi.get("schedules"),
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
