# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.delhaize.be/?operationName=GetStoreSearch&variables=%7B%22pageSize%22%3A900%2C%22lang%22%3A%22nl%22%2C%22query%22%3A%22%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22611d08fab1e7b40c82c9130355453ebb74a30a00eb708c7af6be46ec8fbef330%22%7D%7D"
    domain = "delhaize.be/nl/about-delhaize/our-brands/shop-and-go"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    data = session.get(start_url, headers=hdr).json()
    for poi in data["data"]["storeSearchJSON"]["stores"]:
        street_address = poi["address"]["line1"]
        if poi["address"]["line2"]:
            street_address += " " + poi["address"]["line2"]
        hoo = []
        for e in poi["openingHours"]["groceryOpeningList"]:
            if e["closed"]:
                hoo.append(f'{e["weekDay"]}: closed')
            else:
                closes = e["closingTime"].split()[-1][:-3]
                opens = e["openingTime"].split()[-1][:-3]
                hoo.append(f'{e["weekDay"]}: {opens} - {closes}')
        hoo = " ".join(hoo)
        page_url = "https://www.delhaize.be/storedetails/" + poi["urlName"]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["localizedName"],
            street_address=street_address,
            city=poi["address"]["town"],
            state="",
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["country"]["name"],
            store_number=poi["id"],
            phone=poi["address"]["phone"],
            location_type=poi["groceryStoreType"],
            latitude=poi["geoPoint"]["latitude"],
            longitude=poi["geoPoint"]["longitude"],
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
