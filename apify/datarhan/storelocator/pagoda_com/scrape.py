import re
import ssl
import demjson3
import urllib.parse
from lxml import etree
from time import sleep
from random import uniform

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from tenacity import retry
from tenacity.stop import stop_after_attempt

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


@retry(stop=stop_after_attempt(3))
def fetch(url, session):
    return session.get(url)


def fetch_data():
    domain = "pagoda.com"
    start_url = "https://www.pagoda.com/store-finder/view-all-states"

    session = SgRequests()
    response = fetch(start_url, session)
    dom = etree.HTML(response.text)

    all_states = dom.xpath(
        '//h1[contains(text(), "View All Stores")]/following-sibling::div[1]//a/@href'
    )
    for state_url in all_states:
        sleep(uniform(0, 10))
        full_state_url = urllib.parse.urljoin(start_url, state_url)
        state_response = fetch(full_state_url, session)
        if state_response.status_code == 503:
            continue
        state_dom = etree.HTML(state_response.text)

        all_stores = state_dom.xpath(
            '//div[@class="inner-container storefinder-details view-all-stores"]/div[1]/div[@id]'
        )
        for store_data in all_stores:
            store_url = store_data.xpath(".//a/@href")
            if store_url and "/store/null" not in store_url:
                sleep(uniform(0, 10))
                store_url = urllib.parse.urljoin(start_url, store_url[0])
                store_name_fromlist = store_data.xpath(".//a/text()")
                location_type = "<MISSING>"
                store_response = fetch(store_url, session)
                store_dom = etree.HTML(store_response.text)
                data = store_dom.xpath(
                    '//script[contains(text(), "storeInformation")]/text()'
                )
                if not data:
                    continue
                data = re.findall(
                    "storeInformation = (.+);", data[0].replace("\n", "")
                )[0]
                data = demjson3.decode(data)

                store_number = data["name"]
                if not store_number:
                    store_number = SgRecord.MISSING
                location_name = store_dom.xpath('//h1[@itemprop="name"]/text()')
                if not location_name:
                    location_name = store_name_fromlist
                location_name = location_name[0] if location_name else "<MISSING>"
                street_address = store_data.xpath(
                    './/span[@itemprop="streetAddress"]/text()'
                )
                street_address = (
                    street_address[0].strip().replace("   ", " ")
                    if street_address
                    else "<MISSING>"
                )
                city = store_dom.xpath('//span[@itemprop="addressLocality"]/text()')
                city = city[0] if city else "<MISSING>"
                state = store_dom.xpath('//span[@itemprop="addressRegion"]/text()')
                state = state[0] if state else "<MISSING>"
                zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')
                zip_code = zip_code[0] if zip_code else "<MISSING>"
                phone = store_dom.xpath('//span[@itemprop="telephone"]/a/text()')
                phone = phone[0] if phone else "<MISSING>"
                country_code = store_dom.xpath(
                    '//span[@itemprop="addressCountry"]/text()'
                )
                country_code = country_code[0] if country_code else "<MISSING>"
                latitude = data["latitude"]
                latitude = latitude if latitude else "<MISSING>"
                longitude = data["longitude"]
                longitude = longitude if longitude else "<MISSING>"

                hoo = []
                for day, hours in data["openings"].items():
                    hoo.append(f"{day} {hours}")
                hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
            else:
                store_url = "<MISSING>"
                location_type = "<MISSING>"
                store_number = "<MISSING>"
                location_name = store_data.xpath(".//a/text()")
                location_name = location_name[0] if location_name else "<MISSING>"
                street_address = store_data.xpath(
                    './/span[@itemprop="streetAddress"]/text()'
                )
                street_address = street_address[0] if street_address else "<MISSING>"
                city = store_data.xpath('.//span[@itemprop="addressLocality"]/text()')
                city = city[0] if city else "<MISSING>"
                state = store_data.xpath('.//span[@itemprop="addressRegion"]/text()')
                state = state[0] if state else "<MISSING>"
                zip_code = store_data.xpath('.//span[@itemprop="postalCode"]/text()')
                zip_code = zip_code[0] if zip_code else "<MISSING>"
                phone = store_data.xpath('.//span[@itemprop="telephone"]/text()')
                phone = phone[0] if phone else "<MISSING>"
                country_code = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"
            if location_name == "<MISSING>":
                continue

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
