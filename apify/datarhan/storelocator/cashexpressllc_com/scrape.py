from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.cashexpressllc.com/storelocator/getstores"
    domain = "cashexpressllc.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "txtLocation": "",
        "selDistance": "5",
        "txtLat": "",
        "txtLng": "",
        "add1": "",
        "city": "",
        "statename": "",
        "zip": "",
    }
    data = session.post(start_url, headers=hdr, data=frm).json()

    for poi in data["stores"]:
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        hoo = []
        hoo_raw = {}
        for key, time in poi.items():
            if "open" in key:
                day = key.split("_")[0]
                if hoo_raw.get(day):
                    hoo_raw[day]["open"] = time
                else:
                    hoo_raw[day] = {}
                    hoo_raw[day]["open"] = time
            if "close" in key:
                day = key.split("_")[0]
                if hoo_raw.get(day):
                    hoo_raw[day]["close"] = time
                else:
                    hoo_raw[day] = {}
                    hoo_raw[day]["close"] = time
        for day, hours in hoo_raw.items():
            hoo.append(f'{day} {hours["open"][:-3]} - {hours["close"][:-3]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.cashexpressllc.com/store-locator",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=poi["store_id"],
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
