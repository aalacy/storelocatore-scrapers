import re
import json
import demjson
import yaml
from yaml import FullLoader
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "sixt.co.uk"
    start_url = "https://www.sixt.co.uk/car-hire/united-kingdom/"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//div[@class="swiper-wrapper"]/a/@href')
    for url in all_cities:
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)
        data = dom.xpath('//script[contains(text(), "googleMarkers")]/text()')[0]
        data = re.findall("googleMarkers =(.+);", data.replace("\n", ""))[0]
        data = yaml.load(
            data.replace(" + ", "").replace("\n", "").replace("'", ""),
            Loader=FullLoader,
        )
        for elem in data:
            all_locations.append(elem["locationLink"])

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "mainEntityOfPage")]/text()')
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressRegion"]
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = poi["openingHours"]
            hours_of_operation = " ".join(hoo) if hoo else ""
        else:
            location_name = loc_dom.xpath(
                '//span[@class="dropdown-block_title-copy"]/text()'
            )
            location_name = location_name[0] if location_name else ""
            raw_address = loc_dom.xpath(
                '//div[h3[contains(text(), "location address")]]/following-sibling::div[1]/p/text()'
            )[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            zip_code = addr.postcode
            country_code = loc_dom.xpath('//meta[@name="countrycode"]/@content')
            country_code = country_code[0] if country_code else ""
            location_type = ""

            data = loc_dom.xpath('//script[contains(text(), "googleMarkers")]/text()')[
                0
            ]
            data = re.findall("googleMarkers = (.+);", data)[0]
            data = demjson.decode(data.replace("' + '", ""))
            for e in data:
                if e["locationName"] == location_name:
                    geo = e["coordinates"]
                    break
            latitude = geo["lat"]
            longitude = geo["lng"]
            hoo = loc_dom.xpath('//div[@class="openhours-scheduler"]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""
        hours_of_operation = (
            hours_of_operation.replace("24 HRS RETURN ", "")
            .split("return ")[-1]
            .split("RETURN")[-1]
            .split("HOLIDAY")[0]
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone="",
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
