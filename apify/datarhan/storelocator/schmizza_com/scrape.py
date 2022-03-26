from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "schmizza.com"
    start_url = "https://schmizza.com/modules/multilocation/?near_location=90210&threshold=4000&geocoder_region=&limit=20&services__in=&language_code=en-us&published=1&within_business=true"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/plain, */*",
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["objects"]:
        page_url = "https://" + poi["location_url"]
        phone = poi["phones"][0]["number"]
        hoo = []
        for e in poi["formatted_hours"]["primary"]["grouped_days"]:
            hoo.append(f'{e["label"]}: {e["content"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["location_name"],
            street_address=poi["formatted_address"].split(",")[0],
            city=poi["city"],
            state=poi["state_name"],
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=phone,
            location_type="",
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
