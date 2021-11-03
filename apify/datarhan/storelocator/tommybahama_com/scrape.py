import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "tommybahama.com"
    start_url = "https://www.tommybahama.com/en/store-finder?q=&searchStores=true&searchRestaurants=false&searchOutlets=true&searchInternational=true"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="store-finder-results-title"]/@href')
    next_page = dom.xpath('//a[contains(text(), "Next")]/@href')
    while next_page:
        page_url = "https://www.tommybahama.com" + next_page[0]
        page_response = session.get(page_url)
        page_dom = etree.HTML(page_response.text)
        all_locations += page_dom.xpath(
            '//a[@class="store-finder-results-title"]/@href'
        )
        next_page = page_dom.xpath('//a[contains(text(), "Next")]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url.split("?")[0])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//a/img[contains(@alt, "taken you slightly off course")]'):
            continue

        raw_address = loc_dom.xpath(
            '//div[@class="store-locator-details"]/div[1]//text()'
        )
        raw_address = [e.replace("\xa0", " ").strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        location_name = loc_dom.xpath("//h1/text()")[0]
        street_address = raw_address[0]
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = re.findall(
            "storeaddresscountryname = '(.+?)';", loc_response.text
        )
        country_code = country_code[0] if country_code else ""
        if not country_code and (zip_code and len(zip_code) == 5):
            country_code = "United States"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall("storelatitude = '(.+?)';", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall("storelongitude = '(.+?)';", loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//div[contains(text(), "Store Hours")]/following-sibling::div/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("Hours: ")[-1].split("This location")[0].strip()
        hours_of_operation = (
            hoo.split("Open to a limited")[0].strip() if hoo else "<MISSING>"
        )
        hours_of_operation = hours_of_operation.split(" Happy")[0]
        hours_of_operation = hours_of_operation.split(" Seating")[0]
        if "temporarily" in hours_of_operation:
            hours_of_operation = "Temporarily Closed"
        hours_of_operation = hours_of_operation.replace("|", "").replace(">br>", "")

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
            raw_address=" ".join(raw_address),
        )

        yield item

    response = session.get(
        "https://www.tommybahama.com/stores-restaurants/international-locations"
    )
    dom = etree.HTML(response.text)
    int_locations = dom.xpath('//p[a[u[contains(text(), "VIEW MAP")]]]')
    for poi_html in int_locations:
        raw_data = poi_html.xpath("text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        for i, e in enumerate(raw_data):
            if len(e.split(".")) > 2 and "(" not in e:
                index = i
                break
        raw_address = ", ".join(raw_data[1:index])
        addr = parse_address_intl(raw_address)
        hoo = " ".join(raw_data).split("Open")[-1].strip()
        if "am-" not in hoo.lower():
            hoo = ""
        phone = [e for e in raw_data if len(e.split(".")) > 2 and "," not in e]
        phone = phone[0] if phone else ""
        if "Dubai" in phone:
            phone = ""
        if "Brisbane" in phone:
            phone = ""
        country_code = addr.country
        zip_code = addr.postcode
        if zip_code and len(zip_code.split()) == 2 and not country_code:
            country_code = "Canada"
        if (zip_code and len(zip_code) == 5) and not country_code:
            country_code = "United States"
        if (zip_code and len(zip_code) < 5) and not country_code:
            country_code = "AU"
        location_name = raw_data[0]
        if not country_code and "Tommy Bahama" in location_name:
            country_code = "UNITED ARAB EMIRATES"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.tommybahama.com/stores-restaurants/international-locations",
            location_name=location_name,
            street_address=raw_data[1],
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
