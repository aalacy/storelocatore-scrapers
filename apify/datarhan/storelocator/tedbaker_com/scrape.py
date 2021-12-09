# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.tedbaker.com/us/json/stores/countries"
    domain = "tedbaker.com"

    data = session.get(start_url).json()
    for e in data["data"]:
        url = f'https://www.tedbaker.com/us/json/stores/for-country?isocode={e["isocode"]}'
        all_locations = session.get(url).json()
        for poi in all_locations["data"]:
            hoo = []
            if poi.get("openingHours"):
                for e in poi["openingHours"]["weekDayOpeningList"]:
                    day = e["weekDay"]
                    if e.get("openingTime"):
                        opens = e["openingTime"]["formattedHour"]
                        closes = e["closingTime"]["formattedHour"]
                        hoo.append(f"{day} {opens} - {closes}")
                    else:
                        hoo.append(f"{day} closed")
                hoo = " ".join(hoo)
            if len(hoo) < 10:
                hoo = ""
            raw_address = poi["address"].get("line1")
            if raw_address and poi["address"].get("line2"):
                raw_address += ", " + poi["address"]["line2"]
            if not raw_address and poi["address"].get("line2"):
                raw_address = poi["address"]["line2"]
            if poi["address"].get("line3"):
                raw_address += ", " + poi["address"]["line3"]
            city = poi["address"].get("town")
            if city:
                raw_address += ", " + city
            zip_code = poi["address"].get("postalCode")
            country_code = poi["address"]["country"]["isocode"]
            state = poi["address"].get("state")
            if state:
                raw_address += ", " + state
            if zip_code:
                raw_address += ", " + zip_code
            if not raw_address:
                continue
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if street_address and addr.street_address_2:
                street_address += ", " + addr.street_address_2
            else:
                street_address = addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.tedbaker.com/us/store-finder",
                location_name=poi["displayName"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                store_number=poi["name"],
                phone=poi["address"].get("phone"),
                location_type=poi.get("storeType", {}).get("name"),
                latitude=poi["geoPoint"]["latitude"],
                longitude=poi["geoPoint"]["longitude"],
                hours_of_operation=hoo,
                raw_address=raw_address,
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
