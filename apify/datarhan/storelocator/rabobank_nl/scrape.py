# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.rabobank.nl/wapi/find-your-bank/locations"
    domain = "rabobank.nl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["locations"]:
        page_url = "https://" + poi["bank"]["website"]
        days = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Satarday",
            "7": "Sunday",
        }
        hoo = []
        for e in poi["bank"]["branches"][0]["trading_hours"]:
            day = days[e["week_day_code"]]
            opens = e["trading_hour_durations"][0]["start_time"][:-3]
            closes = e["trading_hour_durations"][0]["end_time"][:-3]
            hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["owner"],
            street_address=poi["street_address"],
            city=poi["city"],
            state="",
            zip_postal=poi["zip"],
            country_code="NL",
            store_number=poi["bank"]["code"],
            phone="",
            location_type=poi["bank"]["type"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
