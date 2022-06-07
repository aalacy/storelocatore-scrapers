import re
import threading
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

start_url = "https://www.signaturestyle.com/salon-directory.html"
domain = "mastercuts.com"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
}

local = threading.local()


def get_session():
    if not hasattr(local, "session"):
        local.session = SgRequests()

    return local.session


def fetch_location(poi_html, retry=0):
    try:
        session = get_session()
        url = poi_html.xpath("@href")[0]
        raw_address = poi_html.xpath("text()")[0]
        store_number = re.search(r"-(\d+).html", url).group(1)
        page_url = urljoin(start_url, url)
        response = session.get(page_url, headers=headers)

        if response.status_code == 404:
            return None

        loc_dom = etree.HTML(response.text)

        if re.search(
            r"Find a Hair Salon Near You",
            loc_dom.xpath("//title/text()")[0],
            re.IGNORECASE,
        ):
            return None

        location_name = loc_dom.xpath("//h2/text()")
        location_name = location_name[0]
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else ""
        if not street_address:
            street_address = raw_address.split(", ")[1]
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else ""
        if not city:
            city = raw_address.split(", ")[2]
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else ""
        if not state:
            state = raw_address.split(", ")[3].split()[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else ""
        if not zip_code:
            zip_code = raw_address.split(", ")[3].split()[1]
        phone = loc_dom.xpath('//a[@id="sdp-phone"]/text()')
        phone = phone[0] if phone else ""
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')

        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath('//div[contains(@class,"salon-timings")]//span')

        hours_of_operation = []
        for dayhour in hoo:
            if "closedNow" in dayhour.attrib["class"]:
                continue

            day = dayhour.xpath('div[contains(@class, "week-day")]/text()')[0]
            hour = dayhour.xpath('div[contains(@class, "oper-hours")]/text()')[0]

            hours_of_operation.append(f"{day}: {hour}")

        hours_of_operation = ",".join(hours_of_operation)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="US",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        return item
    except:
        if retry < 3:
            return fetch_location(poi_html, retry + 1)


def get_state(url, retry=0):
    try:
        session = get_session()
        response = session.get(url)
        dom = etree.HTML(response.text)
        return dom.xpath("//td/a")
    except:
        if retry < 3:
            return get_state(url, retry + 1)


def fetch_data():
    locations = []
    with SgRequests() as session:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_states = dom.xpath('//a[@class="btn btn-primary"]/@href')
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(get_state, urljoin(start_url, url))
                for url in all_states
            ]
            for future in as_completed(futures):
                locations.extend(future.result())

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(fetch_location, poi_html) for poi_html in locations
            ]
            for future in as_completed(futures):
                poi = future.result()
                if poi:
                    yield poi


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
