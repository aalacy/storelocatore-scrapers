from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "abraauto.com"
    start_url = "https://dbripcstage2.interplay.iterate.ai/api/v1/abra/allstores"

    frm = {"lat": 35.562, "lng": -77.4045}
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "apiKey": "1234AKIAVAOWLJICABYD4CDQhjhjhfjdkm",
    }
    data = session.post(start_url, json=frm, headers=hdr).json()
    for poi in data["store"]:
        hoo = []
        for day, hours in poi["hours"].items():
            if hours["is_open"] == 1:
                opens = hours["open"]
                closes = hours["close"]
                hoo.append(f"{day}: {opens} - {closes}")
            else:
                hoo.append(f"{day}: closed")
        hoo = " ".join(hoo)
        state = poi["store_state"]
        city = poi["store_city"]
        zip_code = poi["store_postcode"]
        store_number = poi["store_id"]
        page_url = f"https://www.abraauto.com/location/{state.lower()}/{city.lower()}/{store_number}/"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["store_name"],
            street_address=poi["store_address"],
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=poi["store_phone"],
            location_type="",
            latitude=poi["store_lat"],
            longitude=poi["store_long"],
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
