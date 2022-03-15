import re
import ssl
import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    session = SgRequests()
    domain = "leavetheherdbehind.com"
    start_urls = {
        "France": "https://leavetheherdbehind.com/blogs/locations/tagged/country-france",
        "England": "https://leavetheherdbehind.com/blogs/locations/tagged/country-england",
        "Philippines": "https://leavetheherdbehind.com/blogs/locations/tagged/country-philippines",
        "Scotland": "https://leavetheherdbehind.com/blogs/locations/tagged/country-scotland",
    }
    for country_code, start_url in start_urls.items():
        response = session.get(start_url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[@class="single-location__image"]/@href')
        for store_url in all_locations:
            store_url = urljoin(start_url, store_url)
            with SgFirefox() as driver:
                driver.get(store_url)
                loc_dom = etree.HTML(driver.page_source)

            closed = loc_dom.xpath(
                '//span[contains(text(), "We are now temporarily closed")]'
            )
            location_type = ""
            if closed:
                location_type = "temporarily closed"

            location_name = loc_dom.xpath(
                '//h1[@class="hero__title title-lg location-title-label"]/span/text()'
            )
            location_name = location_name[0] if location_name else "<MISSING>"
            address_raw = loc_dom.xpath("//address/p/text()")
            addr = parse_address_intl(" ".join(address_raw))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address = addr.street_address_1 + " " + addr.street_address_2
            street_address = street_address if street_address else "<MISSING>"
            city = addr.city
            city = city if city else ""
            if not city:
                if len(address_raw) > 2:
                    city = address_raw[-2]
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            if zip_code == "<MISSING>":
                if len(" ".join(address_raw).split(", ")) == 3:
                    zip_code = " ".join(address_raw).split(", ")[-1]

            geo_data = loc_dom.xpath('//script[contains(text(), "center:")]/text()')
            latitude = ""
            longitude = ""
            if geo_data:
                geo = re.findall(r"center: \[(.+?)\],", geo_data[0])
                if geo:
                    geo = geo[0].split(",")
                    latitude = geo[1]
                    longitude = geo[0]
                else:
                    geo = re.findall(r"center: (.+?}),", geo_data[0])[0]
                    geo = demjson.decode(geo)
                    latitude = geo["lat"]
                    longitude = geo["lng"]
            hours_of_operation = loc_dom.xpath('//p[@class="day"]//text()')
            if not hours_of_operation:
                hours_of_operation = loc_dom.xpath(
                    '//h2[contains(text(), "Opening Hours")]/following-sibling::div/span/text()'
                )
            if not hours_of_operation:
                hours_of_operation = loc_dom.xpath(
                    '//h2[contains(text(), "opening hours")]/following-sibling::div/span/text()'
                )
            if not hours_of_operation:
                hours_of_operation = loc_dom.xpath(
                    '//h2[contains(text(), "OPENING HOURS")]/following-sibling::div/span/text()'
                )
            if not hours_of_operation:
                hours_of_operation = loc_dom.xpath(
                    '//h2[contains(text(), "opening hours")]/following-sibling::div//p//text()'
                )
                hours_of_operation = [
                    elem.strip()
                    for elem in hours_of_operation
                    if elem.strip() and "am" in elem
                ]
            if not hours_of_operation:
                hours_of_operation = loc_dom.xpath(
                    '//h2[contains(text(), "OPENING HOURS")]/following-sibling::div[1]//p/text()'
                )
            if not hours_of_operation:
                hours_of_operation = []
                id_data = loc_dom.xpath('//script[contains(text(), "var id")]/text()')
                if not id_data:
                    continue
                store_id = re.findall(r"var id=\'(\d+)\'", id_data[0])[0]
                hoo_response = session.get(
                    f"https://backend.cheerfy.com/shop-service/timetable/?scope_locations={store_id}"
                )
                hoo = demjson.decode(hoo_response.text)
                for elem in hoo["timetable"]:
                    day = elem["day"]
                    opens = elem["intervals"][0]["open_at"]
                    closes = elem["intervals"][0]["close_at"]
                    hours_of_operation.append(f"{day} {opens} - {closes}")
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )
            hours_of_operation = (
                hours_of_operation
                if hours_of_operation and hours_of_operation.strip()
                else "<MISSING>"
            )
            if hours_of_operation == "Opening Hours will be published soon.":
                continue
            if "Unit 5/6" in address_raw[0]:
                street_address = "Unit 5/6, Windsor Royal Station Shopping Centre"
                zip_code = "SL4 1PJ"
            if hours_of_operation == "We are now temporarily closed":
                hours_of_operation = "temporarily closed"

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone="",
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(address_raw),
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
