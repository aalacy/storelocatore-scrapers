# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.beta.thirstycamel.com.au/stores/all?limit=10&page=1"
    domain = "thirstycamel.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        page_url = f"https://www.thirstycamel.com.au/stores/{poi['slug']}"
        hoo = []
        if poi["hours"]:
            for day, hours in poi["hours"].items():
                if day == "id":
                    continue
                if hours:
                    hoo.append(f"{day}: {hours[0]} - {hours[1]}")
                else:
                    hoo.append(f"{day}: closed")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"].split(", ")[0],
            city=poi["address"].split(", ")[-1],
            state=poi["region"],
            zip_postal=poi["postcode"],
            country_code="AU",
            store_number=poi["legacyStoreId"],
            phone=poi["phoneNumber"],
            location_type="",
            latitude=poi["point"]["coordinates"][0],
            longitude=poi["point"]["coordinates"][1],
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
