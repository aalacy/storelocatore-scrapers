from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "colehaan.com"
    start_url = "https://stores.colehaan.com/index.html"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_countries = dom.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for url in all_countries:
        country_url = urljoin(start_url, url)
        response = session.get(country_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="location-list-locations-wrapper"]/div')
        for poi_html in all_locations:
            country_code = country_url.split("/")[-1].split(".")[0].upper()
            store_url = country_url
            own_url = poi_html.xpath(
                './/h5[@class="c-location-grid-item-title"]/a/@href'
            )
            if own_url:
                store_url = urljoin(start_url, own_url[0])
            location_name = " ".join(
                poi_html.xpath('.//h5[@class="c-location-grid-item-title"]//text()')
            )
            street_address = poi_html.xpath(
                './/span[@class="c-address-street c-address-street-1"]/text()'
            )[0]
            str_adr_2 = poi_html.xpath(
                './/span[@class="c-address-street c-address-street-2"]/text()'
            )
            if str_adr_2:
                street_address += " " + str_adr_2[0]
            city = poi_html.xpath('.//span[@class="c-address-city"]/span/text()')[0]
            if city.endswith(","):
                city = city[:-1]
            state = poi_html.xpath('.//span[@class="c-address-state"]/text()')
            state = state[0].strip() if state else "<MISSING>"
            zip_code = poi_html.xpath('.//span[@class="c-address-postal-code"]/text()')
            zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath(
                './/div[@class="c-location-grid-item-phone"]//span/text()'
            )
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = []
            hours_html = poi_html.xpath(".//div[@data-day-of-week-start-index]")
            if hours_html:
                days = [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
                for i, day in enumerate(days):
                    hours = hours_html[i].xpath(".//text()")
                    hours = [e.strip() for e in hours if e.strip()]
                    hours = " ".join(hours)
                    hoo.append(f"{day} {hours}")
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
