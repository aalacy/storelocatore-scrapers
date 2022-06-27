# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=SWRKLBDFQWBVUQNW&center=42.633107705427925,-79.68065119667432&coordinates=23.35285411214062,-48.12791682167432,61.91336129871523,-111.23338557167432&multi_account=false&page={}&pageSize=100"
    domain = "goldenkrust.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for p in range(1, 101):
        all_locations = session.get(start_url.format(p), headers=hdr).json()
        if not all_locations:
            break
        for poi in all_locations:
            poi = poi["store_info"]
            hoo_data = poi["store_hours"].split(";")
            days_dict = {
                "7": "Sunday",
                "1": "Monday",
                "2": "Tuesday",
                "3": "Wednesday",
                "4": "Thursday",
                "5": "Friday",
                "6": "Saturday",
            }
            hoo = []
            for e in hoo_data:
                if e:
                    e_data = e.split(",")
                    day = days_dict[e_data[0]]
                    opens = e_data[1][:-2] + ":" + e_data[1][-2:]
                    closes = e_data[2][:-2] + ":" + e_data[2][-2:]
                    hoo.append(f"{day}: {opens} - {closes}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["website"],
                location_name=poi["name"],
                street_address=poi["address"],
                city=poi["locality"],
                state=poi["region"],
                zip_postal=poi["postcode"],
                country_code=poi["country"],
                store_number=poi["corporate_id"],
                phone=poi["phone"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
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
