import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    scraped_urls = []
    domain = "orkin.com"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    session = SgRequests()
    start_url = "https://www.orkin.com/locations"
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    allstates_urls = dom.xpath(
        '//a[contains(@class, "chakra-link cta cta--ghost-dark")]/@href'
    )
    for state_url in allstates_urls:
        full_state_url = urljoin(start_url, state_url)
        if full_state_url in scraped_urls:
            continue

        state_response = session.get(full_state_url.replace(" ", ""), headers=headers)
        scraped_urls.append(full_state_url)
        state_dom = etree.HTML(state_response.text)

        allcities_urls = state_dom.xpath(
            '//a[contains(@class, "chakra-link cta cta--ghost-dark")]/@href'
        )
        for city_url in allcities_urls:
            full_city_url = urljoin(start_url, city_url)
            if full_city_url in scraped_urls:
                continue
            city_response = session.get(full_city_url.replace(" ", ""), headers=headers)
            scraped_urls.append(full_city_url)
            city_dom = etree.HTML(city_response.text)
            all_locations = city_dom.xpath('//a[contains(@href, "branch")]/@href')
            for page_url in all_locations:
                page_url = urljoin(start_url, page_url)
                if page_url in scraped_urls:
                    continue
                scraped_urls.append(page_url)
                loc_response = session.get(page_url, headers=headers)
                code = loc_response.status_code
                while code != 200:
                    session = SgRequests()
                    loc_response = session.get(page_url, headers=headers)
                    code = loc_response.status_code
                loc_dom = etree.HTML(loc_response.text)
                poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')[
                    0
                ]
                poi = json.loads(poi)

                location_name = loc_dom.xpath("//h1/text()")[0]
                hoo = []
                for day in poi["openingHoursSpecification"]["dayOfWeek"]:
                    hoo.append(
                        f"{day} {poi['openingHoursSpecification']['opens']} {poi['openingHoursSpecification']['closes']}"
                    )
                hoo = " ".join(hoo)

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=poi["address"]["postalCode"],
                    country_code=poi["address"]["addressCountry"],
                    store_number="",
                    phone=poi["telephone"],
                    location_type=poi["@type"],
                    latitude=poi["geo"]["latitude"],
                    longitude=poi["geo"]["longitude"],
                    hours_of_operation=hoo,
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
