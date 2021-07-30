import re
import ssl
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://locations.cinnabon.com/index.html"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = []
    all_states = dom.xpath('//a[@class="Directory-listLink"]')
    for state_html in all_states:
        total = int(state_html.xpath("@data-count")[0][1:-1])
        url = state_html.xpath("@href")
        if total == 1:
            all_locations += url
            continue
        response = session.get(urljoin(start_url, url[0]), headers=hdr)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//a[@class="Directory-listLink"]')
        for city_html in all_cities:
            total = int(city_html.xpath("@data-count")[0][1:-1])
            url = city_html.xpath("@href")
            if total == 1:
                all_locations += url
                continue

            response = session.get(urljoin(start_url, url[0]), headers=hdr)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@data-ya-track="visitpage"]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        if store_url == "https://locations.cinnabon.com/":
            continue
        if url.endswith(".") and not store_url.endswith("."):
            store_url += "."
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath(
            '//div[@class="Core-infoContent"]//div[@itemprop="telephone"]/text()'
        )
        phone = phone[0] if phone else SgRecord.MISSING
        location_type = SgRecord.MISSING
        temp = loc_dom.xpath('//h2[@class="Core-title"]/text()')
        if temp and "Temporarily Closed" in temp[0]:
            location_type = "Temporarily Closed"
        hoo = loc_dom.xpath('//script[@class="js-hours-config"]/text()')
        hours = []
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
            location_name=loc_dom.xpath('//a[@class="Hero-geoText"]/text()')[0],
            street_address=loc_dom.xpath(
                '//div[@class="Core-infoContent"]//span[@class="c-address-street-1"]/text()'
            )[0],
            city=loc_dom.xpath(
                '//div[@class="Core-infoContent"]//span[@class="c-address-city"]/text()'
            )[0],
            state=loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')[0],
            zip_postal=loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0],
            country_code=loc_dom.xpath(
                '//div[@class="Core-infoContent"]//address/@data-country'
            )[0],
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0],
            longitude=loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0],
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
