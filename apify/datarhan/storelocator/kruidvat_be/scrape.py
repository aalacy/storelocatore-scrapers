# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.kruidvat.be/api/v2/kvb/stores?lang=fr_BE&radius=100000&pageSize=10000&fields=FULL"
    domain = "kruidvat.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["stores"]:
        base_url = "https://www.kruidvat.be/fr/recherchemagasin"
        page_url = urljoin(base_url, poi["url"])
        hoo = []
        for e in poi["openingHours"]["weekDayOpeningList"]:
            day = e["weekDay"]
            if e.get("closed"):
                hoo.append(f"{day}: closed")
            else:
                opens = e["openingTime"]["formattedHour"]
                closes = e["closingTime"]["formattedHour"]
                hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)
        latitude = poi["geoPoint"]["latitude"]
        latitude = latitude if latitude and latitude != "0.0" else ""
        longitude = poi["geoPoint"]["longitude"]
        longitude = longitude if longitude and longitude != "0.0" else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"]["line1"],
            city=poi["address"]["town"],
            state=poi["address"].get("province"),
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["country"]["isocode"],
            store_number="",
            phone="",
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
