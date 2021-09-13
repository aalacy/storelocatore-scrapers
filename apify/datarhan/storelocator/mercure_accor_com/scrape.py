import json
from lxml import etree
from urllib.parse import urlencode

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def parse_ids(dom, session):
    ent_list = []
    ids = dom.xpath('//script[@id="paginator-ids-core"]/text()')
    urls = []
    if ids:
        ids = json.loads(ids[0])
        for e in ids:
            ent_list.append({"meta.id": {"$eq": e}})

        params = {
            "api_key": "f60a800cdb7af0904b988d834ffeb221",
            "v": "20160822",
            "filter": {"$or": ent_list},
            "languages": "en_GB",
            "limit": "50",
        }
        params = urlencode(params)
        url = "https://liveapi.yext.com/v2/accounts/1624327134898036854/entities?"

        urls = []
        data = session.get(url + params).json()
        for e in data["response"]["entities"]:
            urls.append(e["c_pageDestinationURL"])

    return urls


def fetch_all_locations(session):
    locations = []
    start_url = "https://all.accor.com/gb/world/hotels-accor-monde.shtml"
    traverse_directory(start_url, session, locations)

    return locations


def traverse_directory(url, session, locations):
    page = etree.HTML(session.get(url, headers=headers, timeout=180).text)
    sublocations = page.xpath('//*[@class="Teaser-link"]/@href')
    bookings = [url for url in sublocations if "index.en.shtml" in url]
    if len(bookings):
        for booking in bookings:
            if booking not in locations:
                locations.append(booking)
    else:
        for location in sublocations:
            traverse_directory(location, session, locations)


def fetch_data():
    domain = "accor.com"
    session = SgRequests(proxy_rotation_failure_threshold=3, retry_behavior=None)

    all_locations = fetch_all_locations(session)
    for store_url in all_locations:
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "addressCountry")]/text()'
        )
        if not poi:
            continue
        poi = json.loads(poi[0])

        street_address = loc_dom.xpath(
            '//meta[@property="og:street-address"]/@content'
        )[0]
        latitude = loc_dom.xpath('//meta[@property="og:latitude"]/@content')
        latitude = latitude[0] if latitude else SgRecord.MISSING
        longitude = loc_dom.xpath('//meta[@property="og:longitude"]/@content')
        longitude = longitude[0] if longitude else SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["name"],
            street_address=street_address,
            city=poi["address"].get("addressLocality"),
            state=SgRecord.MISSING,
            zip_postal=poi["address"].get("postalCode"),
            country_code=poi["address"]["addressCountry"],
            store_number=SgRecord.MISSING,
            phone=poi.get("telephone"),
            location_type=poi["@type"],
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        yield item


def write_output(data):
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for row in data:
            writer.write_row(row)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
