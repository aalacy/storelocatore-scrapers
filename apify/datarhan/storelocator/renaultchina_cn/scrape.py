# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://www.renaultchina.cn/mapRenault.html"
    domain = "renaultchina.cn"
    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/json;charset=utf8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    all_cities = session.get(
        "https://www.renaultchina.cn/api/front/network/get_province_city", headers=hdr
    ).json()
    for e in all_cities["data"]:
        url = "https://www.renaultchina.cn/api/front/network/get_agency_list"
        for c in e["citys"]:
            frm = {"param": [e["province"], c]}
            data = session.post(url, json=frm, headers=hdr).json()

            for poi in data["data"]:
                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name=poi["name"],
                    street_address=poi["address"],
                    city=poi["city"],
                    state=e["province"],
                    zip_postal="",
                    country_code="CN",
                    store_number=poi["id"],
                    phone=poi["mobile"].split("/")[0],
                    location_type="",
                    latitude=poi["lat"],
                    longitude=poi["lng"],
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
