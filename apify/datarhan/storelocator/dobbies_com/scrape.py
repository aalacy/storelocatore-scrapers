import ssl
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    session = SgRequests()

    domain = "dobbies.com"
    start_url = "https://www.dobbies.com/store-locator"

    params = {"latitude": 50.1109, "longitude": 8.6821, "accuracy": 100}

    with SgChrome() as driver:
        driver.execute_cdp_cmd("Page.setGeolocationOverride", params)
        driver.get(start_url)
        sleep(20)
        driver.find_element_by_xpath(
            '//div[@class="ms-store-select__search-see-all-stores"]'
        ).click()
        sleep(5)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath(
        '//a[@class="ms-store-select__location-line-shop-link"]/@href'
    )
    for store_url in list(set(all_locations)):
        if store_url == "https://www.dobbies.com/atherstone-outlet":
            store_url = "https://www.dobbies.com/atherstone"
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="ms-content-block__title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_adr = loc_dom.xpath(
            '//h4[contains(text(), "Address")]/following-sibling::p[1]/text()'
        )[0]
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]//text()')
        phone = phone[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        tmp_closed = loc_dom.xpath(
            '//h3[contains(text(), "Our restaurant is temporarily closed")]'
        )
        if tmp_closed:
            location_type = "temporarily closed"
        if loc_dom.xpath('//p[contains(text(), "temporarily closed")]'):
            location_type = "temporarily closed"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        geo = loc_dom.xpath('//a[contains(@href, "maps")]/@href')
        if geo:
            if "/@" in geo[0]:
                geo = geo[0].split("/@")[-1].split(",")[:2]
                latitude = geo[0]
                longitude = geo[1]
        hours_of_operation = loc_dom.xpath(
            '//h3[contains(text(), "Store opening hours")]/following-sibling::ul/li//text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if street_address == "Surrey Sm6 0Su Woodmansterne Lane":
            street_address = "Surrey Woodmansterne Lane"
            zip_code = "SM6 0SU"
        if street_address == "Lincs Pe21 9Rz Wainfleet Road":
            street_address = "Lincs Wainfleet Road"
            zip_code = "PE21 9RZ"
        if street_address == "Dd5 4Hb Ethiebeaton Park":
            street_address = "Ethiebeaton Park"
            zip_code = "DD5 4HB"

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
