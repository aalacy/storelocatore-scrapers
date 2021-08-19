import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://eu.christianlouboutin.com/fr_fr/storelocator/all-stores"
    domain = "christianlouboutin.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = []
    all_urls = dom.xpath('//h4[@class="country-name"]/a/@href')
    for url in all_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//li[@class="city"]/ul/li/a/@href')

    for store_url in all_locations:
        if store_url == "https://eu.christianlouboutin.com/fr_fr/store/":
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
        if not poi:
            continue
        poi = json.loads(poi[0])

        location_name = poi["name"]
        street_address = poi["address"]["streetAddress"]
        city = SgRecord.MISSING
        if poi["address"]["addressLocality"]:
            city = poi["address"]["addressLocality"].split(",")[0].strip()
        state = SgRecord.MISSING
        if "NY" in city:
            city = city.replace("NY", "").strip()
            state = "NY"
        zip_code = poi["address"].get("postalCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        street_address = street_address.replace(zip_code, "").strip()
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for e in poi["openingHoursSpecification"]:
            day = e["dayOfWeek"]
            opens = e["opens"]
            closes = e["closes"]
            hoo.append(f"{day} {opens} - {closes}")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
