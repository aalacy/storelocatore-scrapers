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
    domain = "aerotek.com"
    start_urls = [
        "https://www.aerotek.com/en/locations/canada",
        "https://aerotek.com/en/locations/united-states",
        "https://www.aerotek.com/en-gb/locations/emea/united-kingdom",
    ]

    for url in start_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        country_urls = dom.xpath('//div[@id="location-title"]/a/@href')
        for poi_url in country_urls:
            page_url = urljoin(url, poi_url)
            store_response = session.get(page_url)
            store_dom = etree.HTML(store_response.text)

            location_name = store_dom.xpath('//div[@id="location-title"]/a/text()')[0]
            street_address = store_dom.xpath(
                '//span[@class="acs-location-address"]/text()'
            )[0]
            street_address_2 = store_dom.xpath(
                '//spa[@class="acs-location-address2"]/text()'
            )
            if street_address_2:
                street_address += ", " + street_address_2
            city = (
                store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                .split(",")[0]
                .strip()
            )
            country_code = store_dom.xpath('//span[@class="acs-country"]/text()')
            country_code = country_code[0] if country_code else ""
            if country_code == "<MISSING>" and "united-kingdom" in url:
                country_code = "United Kingdom"
            if country_code == "Canada":
                state = (
                    store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                    .split(",")[-1]
                    .strip()
                    .split()[:-2]
                )
                state = " ".join(state) if state else ""
                zip_code = (
                    store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                    .split(",")[-1]
                    .strip()
                    .split()[-2:]
                )
                zip_code = " ".join(zip_code) if zip_code else ""
            elif country_code == "United Kingdom":
                state = "<MISSING>"
                zip_code = (
                    store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                    .split(",")[-1]
                    .strip()
                )
            else:
                state = (
                    store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                    .split(",")[-1]
                    .strip()
                    .split()[:-1]
                )
                state = " ".join(state) if state else ""
                if not state:
                    state = (
                        store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                        .split(",")[1]
                        .strip()
                    )
                zip_code = (
                    store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                    .split(",")[-1]
                    .strip()
                    .split()[-1:]
                )
                zip_code = " ".join(zip_code) if zip_code else ""
            phone = store_dom.xpath('//span[@class="acs-location-phone"]/a/text()')
            phone = phone[0] if phone else ""

            store_data = store_dom.xpath(
                '//*[contains(@data-ux-args, "Lat")]/@data-ux-args'
            )
            if store_data:
                store_data = json.loads(store_data[0])
                latitude = store_data["MapPoints"][0]["Lat"]
                longitude = store_data["MapPoints"][0]["Long"]
            else:
                latitude = store_dom.xpath(
                    '//div[@id="location-title"]/@data-mappoint'
                )[0].split(",")[0]
                longitude = store_dom.xpath(
                    '//div[@id="location-title"]/@data-mappoint'
                )[0].split(",")[1]
            hours_of_operation = store_dom.xpath(
                '//div[@class="score-content-spot aerotek-location-hours"]//text()'
            )
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
            hours_of_operation = (
                ", ".join(hours_of_operation).replace("Office Hours:,", "").strip()
            )
            if not hours_of_operation:
                hours_of_operation = store_dom.xpath(
                    '//p[contains(text(), "Office Hours:")]/following-sibling::p/text()'
                )
                hours_of_operation = (
                    " ".join(hours_of_operation) if hours_of_operation else ""
                )
            hours_of_operation = hours_of_operation if hours_of_operation else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
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
