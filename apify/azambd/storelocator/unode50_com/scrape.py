import json
from lxml import etree

from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
import requests

url = "https://www.unode50.com/us/stores"
domain = "unode50.com"

headers = {
    "authority": "www.unode50.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.unode50.com/us/stores",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "TvWhqLk3ZpjZqFRioIv7gr5vUZpcsmBd=668f111c445a94ba77d8cb54cd515cf2; ClsK7d1xOIBOgnEV3jdywfE11djIfGXh=dc73442c9d14c88f794251c25da742e1; _gcl_au=1.1.1931177535.1631710688; form_key=faqDWZfxvR835ic2; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; mage-cache-sessid=true; _uetsid=934ec140162411eca711f579476138b2; _uetvid=934ed7e0162411ecb7d9d37758dc3e36; mage-messages=; product_data_storage=%7B%7D; _hjid=da7dbb3b-0f0d-41e6-97dd-6f3a7f37968a; _hjFirstSeen=1; _fbp=fb.1.1631710690060.2138396993; _hjAbsoluteSessionInProgress=0; _pin_unauth=dWlkPU9Ua3hZamt6WTJVdFlUYzJNUzAwTm1VM0xUZzBObUV0TUdNNE5tSXhOVFUxWldZeA; _ga=GA1.2.418090098.1631710693; _gid=GA1.2.8778045.1631710693",
}

response = requests.request("GET", url, headers=headers)


def fetch_data():

    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "calendar")]/text()')[0]
    data = json.loads(data)

    for poi in data["*"]["Magento_Ui/js/core/app"]["components"][
        "store-locator-search"
    ]["markers"]:
        location_name = poi["name"]
        if location_name == "g":
            continue
        if "., .," in poi["address"]:
            continue
        raw_address = poi["address"].replace("\n", ", ").replace("\t", ", ").split(", ")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        city = addr.city
        if not city:
            city = raw_address[-2]
        if city == "-":
            city = SgRecord.MISSING
        street_check = " ".join([e.capitalize() for e in poi["address"].split()]).split(
            city
        )
        if len(street_check) == 2:
            street_address = (
                " ".join([e.capitalize() for e in poi["address"].split()])
                .split(city)[0]
                .strip()
            )
        else:
            street_address = " ".join([e.capitalize() for e in raw_address[0].split()])
        if street_address.endswith(","):
            street_address = street_address[:-1]
        if street_address == "South Market":
            street_address = "South Market, Bay 34"
        if street_address.isdigit():
            street_address = ", ".join(raw_address[:2])
        if street_address in ["-", "."]:
            street_address = SgRecord.MISSING
        street_address = street_address.replace(">> ", "").strip()
        if street_address == "12":
            street_address = ", ".join(raw_address[:2])
        state = addr.state
        zip_code = addr.postcode
        store_number = poi["id"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        store_url = f"https://www.unode50.com/en/int/stores#{latitude},{longitude}"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=poi["address"].replace("\n", ", ").replace("\t", ", "),
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
