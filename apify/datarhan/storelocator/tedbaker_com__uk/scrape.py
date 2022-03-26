import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "tedbaker.com"
    start_url = "https://www.tedbaker.com/uk/json/stores/for-country?isocode=GB"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    response = session.get("https://www.tedbaker.com/uk/store-finder", headers=hdr)
    dom = etree.HTML(response.text)
    token = dom.xpath('//input[@name="CSRFToken"]/@value')[0]

    hdr = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "X-XSRF-TOKEN": token,
    }

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["data"]:
        store_url = "https://www.tedbaker.com/uk/store/{}".format(poi["name"])
        location_name = poi["displayName"]
        street_address = poi["address"]["line1"]
        if poi["address"].get("line2"):
            street_address += ", " + poi["address"]["line2"]
        city = poi["address"].get("town")
        if not city:
            city = poi["address"].get("line3")
        if not city:
            if ", " in street_address:
                city = street_address.split(", ")[-1]
                street_address = street_address.split(", ")[0]
        city = city if city else "<MISSING>"
        city = city.split(",")[0]
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["country"]["isocode"]
        store_number = poi["name"]
        location_type = poi.get("storeType", {}).get("name")
        location_type = location_type if location_type else "<MISSING>"
        phone = poi["address"].get("phone")
        phone = phone if phone else "<MISSING>"
        latitude = poi["geoPoint"]["latitude"]
        longitude = poi["geoPoint"]["longitude"]
        hours_of_operation = []
        if poi.get("openingHours"):
            for elem in poi["openingHours"]["weekDayOpeningList"]:
                if not elem.get("openingTime"):
                    continue
                day = elem["weekDay"]
                opens = elem["openingTime"]["formattedHour"]
                closes = elem["closingTime"]["formattedHour"]
                if not elem["closed"]:
                    hours_of_operation.append(f"{day} {opens} - {closes}")
                else:
                    hours_of_operation.append(f"{day} closed")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
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
