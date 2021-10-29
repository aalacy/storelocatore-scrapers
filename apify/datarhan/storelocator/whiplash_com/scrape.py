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

    start_url = "https://whiplash.com/about/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_regs = dom.xpath('//a[contains(@href, "/location/")]/@href')
    for url in all_regs:
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//i[contains(@class, "fa-map-marker text-orange")]/following-sibling::div[1]'
        )

        data = dom.xpath('//script[contains(@data-schema, "location-App")]/text()')
        if data:
            data = json.loads(data[0])

        for poi_html in all_locations:
            raw_address = poi_html.xpath(".//p/text()")[1:]
            raw_address = [e.strip() for e in raw_address if e.strip()]
            if len(raw_address) == 3:
                raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
            raw_address = [e.strip() for e in raw_address if e.strip()]
            store_url = url
            street_address = raw_address[0]
            city = raw_address[-1].split(", ")[0]
            state = raw_address[-1].split(", ")[-1].split()[0]
            location_name = f"{city}, {state}"
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            for e in data:
                if type(e) == str:
                    continue
                if not e.get("itemReviewed"):
                    if e.get("streetAddress"):
                        if e["streetAddress"].lower() == street_address.lower():
                            name = e["@id"].split("#")[-1].split("Postal")[0]
                            if not name:
                                continue
                            if name[-1].isdigit():
                                name = name[:-1] + " " + name[-1]
                            for s in data:
                                if s["name"] == f"{name} GeoCoordiates":
                                    latitude = s["latitude"]
                                    longitude = s["longitude"]
                                    break
                    else:
                        continue
                if e.get("itemReviewed"):
                    if not e["itemReviewed"]["address"].get("streetAddress"):
                        continue
                    if (
                        street_address.split(", ")[-1].lower()
                        in e["itemReviewed"]["address"]["streetAddress"].lower()
                    ):
                        latitude = e["itemReviewed"]["geo"]["latitude"]
                        longitude = e["itemReviewed"]["geo"]["longitude"]
            if latitude == "<MISSING>" and len(all_locations) == 1:
                data = dom.xpath('//script[contains(text(), "latitude")]/text()')
                if data:
                    data = json.loads(data[0])
                    if type(data) == list:
                        data = data[0]
                    latitude = data["geo"]["latitude"]
                    longitude = data["geo"]["longitude"]
            hours_of_operation = "<MISSING>"

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
