import json
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.5)

    domain = "auntieannes.com"
    user_agent = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "referer": "https://www.auntieannes.com/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }

    start_url = "https://locations.auntieannes.com/"
    response = session.get(start_url, headers=user_agent)
    dom = etree.HTML(response.text)

    all_locations = []
    all_states = dom.xpath('//a[@class="Directory-listLink"]')
    for state in all_states:
        url = state.xpath(".//@href")[0]
        total = int(state.xpath(".//@data-count")[0][1:-1])
        if total == 1:
            all_locations.append(url)
            continue
        full_url = urljoin(start_url, url)
        response = session.get(full_url, headers=user_agent)
        dom = etree.HTML(response.text)

        all_cities = dom.xpath('//a[@class="Directory-listLink"]')
        for city in all_cities:
            url = city.xpath(".//@href")[0]
            total = int(city.xpath(".//@data-count")[0][1:-1])
            if total == 1:
                all_locations.append(url)
                continue
            full_url = urljoin(start_url, url)
            response = session.get(full_url, headers=user_agent)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@class="Link Link--primary"]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//a[@class="Hero-geoText"]/text()')[0]
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')[0]
        city = loc_dom.xpath('//span[@class="c-address-city"]/text()')[0]
        state = loc_dom.xpath('//abbr[@class="c-address-state"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = loc_dom.xpath("//address/@data-country")[0]
        phone = loc_dom.xpath('//div[@id="phone-main"]/text()')
        phone = phone[0] if phone else SgRecord.MISSING
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hours = []
        hoo = loc_dom.xpath('//script[@class="js-hours-config"]/text()')
        if hoo:
            hoo = json.loads(hoo[0])
            for e in hoo["hours"]:
                day = e["day"]
                if e["isClosed"]:
                    hours.append(f"{day} closed")
                else:
                    opens = str(e["intervals"][0]["start"])
                    opens = opens[:-2] + ":" + opens[-2:]
                    closes = str(e["intervals"][0]["end"])
                    closes = closes[:-2] + ":" + closes[-2:]
                    hours.append(f"{day} {opens} - {closes}")
        hours = " ".join(hours) if hours else SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours,
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
