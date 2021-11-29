from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://app.burgerking.co.za/management/api/store/locations"
    domain = "burgerking.co.za"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    data = session.get(start_url, headers=hdr).json()
    for region in data:
        for area in region["Areas"]:
            for store in area["Stores"]:
                store_number = store["Id"]
                page_url = f"https://app.burgerking.co.za/restaurant/{store_number}/{store['Name'].lower().replace(' ', '-')}"
                poi = session.get(
                    f"https://app.burgerking.co.za/management/api/storeinfo?storeId={store_number}"
                ).json()
                addr = parse_address_intl(poi["Address"])
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                hoo = []
                for e in poi["TradingHours"]:
                    day = e["DayAsString"]
                    opens = e["OpenTime"][:-3]
                    closes = e["CloseTime"][:-3]
                    hoo.append(f"{day} {opens} - {closes}")
                hours_of_operation = " ".join(hoo) if hoo else SgRecord.MISSING

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["Name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=addr.country,
                    store_number=store_number,
                    phone=poi["TelephoneNumber"],
                    location_type=SgRecord.MISSING,
                    latitude=poi["Latitude"],
                    longitude=poi["Longitude"],
                    hours_of_operation=hours_of_operation,
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
