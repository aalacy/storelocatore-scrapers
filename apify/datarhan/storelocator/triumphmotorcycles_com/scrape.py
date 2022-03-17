from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "triumphmotorcycles.com"

    start_url = "https://www.triumphmotorcycles.com/api/v2/places/alldealers?LanguageCode=en-US&SiteLanguageCode=en-US&Skip=0&Take=500&CurrentUrl=www.triumphmotorcycles.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["DealerCardData"]["DealerCards"]
    for poi in all_locations:
        page_url = poi["DealerWebsiteUrl"]
        location_name = poi["Title"]

        raw_address = f"{poi['AddressLine1']} {poi['AddressLine2']} {poi['AddressLine3']} {poi['AddressLine4']}"
        addr = parse_address_intl(raw_address.replace("<br/>", " "))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        if not zip_code:
            zip_code = poi["PostCode"]
        country_code = addr.country
        phone = poi["Phone"]
        latitude = poi["Latitude"]
        longitude = poi["Longitude"]
        hoo = []
        if poi["OpeningTimes"]:
            hoo = etree.HTML(poi["OpeningTimes"]).xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = ", ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
