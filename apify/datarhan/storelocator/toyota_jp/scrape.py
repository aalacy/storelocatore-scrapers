from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://toyota.jp/service/store-search/dc/map-search-ajax?smode=dealer"
    domain = "toyota.jp"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["result"]["storeList"]
    for poi in all_locations:
        if not poi["sshSales"]:
            continue
        page_url = "https://toyota.jp/service/store-search/dc/map-search?padid=tjptop_request_storesearch"
        url = f"https://toyota.jp/service/store-search/dc/store-data-ajax?mode=detail&officeCd={poi['saleOfficeCd']}&storeCd={poi['storeCd']}&dispMode=dealer&selectCar="
        poi_data = session.get(url).json()
        poi_data = poi_data["result"]
        hoo = " ".join(poi_data["openHour"])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["storeName"],
            street_address=poi["address"],
            city=poi["prefectureName"],
            state="",
            zip_postal="",
            country_code="JP",
            store_number=poi["storeCd"],
            phone=poi_data["tel"],
            location_type="sshSales",
            latitude=poi["lat"],
            longitude=poi["lon"],
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
