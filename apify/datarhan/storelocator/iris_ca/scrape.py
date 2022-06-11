import re
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://iris.ca/en/find-a-store/"
    domain = "iris.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "__SLS_REDUX_STATE__")]/text()')[0]
    data = re.findall(r"SLS_REDUX_STATE__ =(.+);", data)[0]
    data = json.loads(data)

    all_ids = []
    for elem in data["dataLocations"]["collection"]["features"]:
        all_ids.append(str(elem["properties"]["id"]))

    params = {
        "locale": "en_CA",
        "ids": ",".join(all_ids),
        "clientId": "587e629420d63ace17da9a05",
        "cname": "iris-sweetiq-sls-production.sweetiq.com",
    }
    url = "https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/IVltr82YbCa5QgACToun0x8jstGlTO/locations-details"
    opt_hdr = {
        "Access-Control-Request-Headers": "x-api-key",
        "Access-Control-Request-Method": "GET",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    session.request(url, method="OPTIONS", params=params, headers=opt_hdr)
    data = session.get(url, params=params).json()

    for poi in data["features"]:
        store_url = urljoin(start_url, poi["properties"]["slug"])
        location_name = poi["properties"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["properties"]["addressLine1"]
        if poi["properties"]["addressLine2"]:
            street_address += " " + poi["properties"]["addressLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        city = city if city else "<MISSING>"
        state = poi["properties"]["province"]
        state = state if state else "<MISSING>"
        zip_code = poi["properties"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["properties"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["properties"]["branch"]
        phone = poi["properties"]["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][1]
        longitude = poi["geometry"]["coordinates"][0]
        hoo = []
        for day, hours in poi["properties"]["hoursOfOperation"].items():
            if hours:
                opens = hours[0][0]
                closes = hours[0][1]
                hoo.append(f"{day} {opens} - {closes}")
            else:
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
