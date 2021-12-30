from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://pt.sunglasshut.com/api/content/render/false/limit/9999/type/json/query/+contentType:SghStoreLocator%20+languageId:4%20+deleted:false%20+working:true/orderby/modDate%20desc"
    domain = "pt.sunglasshut.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    all_locations = data["contentlets"]
    for poi in all_locations:
        page_url = f'https://pt.sunglasshut.com/pt/encontre-loja/{poi["seoUrl"]}'
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        hoo = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            hoo.append(f"{day} {poi[day]}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state="",
            zip_postal=poi["zip"],
            country_code="PT",
            store_number="",
            phone=poi["phone"],
            location_type="",
            latitude=poi["geographicCoordinatesLatitude"],
            longitude=poi["geographicCoordinatesLongitude"],
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
