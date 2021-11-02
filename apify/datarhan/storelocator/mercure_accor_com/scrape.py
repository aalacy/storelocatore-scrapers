import json
from bs4 import BeautifulSoup
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


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


def traverse(url, session, locations):
    response = session.get(url, headers=headers)
    try:
        soup = BeautifulSoup(response.text)
    except:
        return

    links = []
    links.extend(soup.find_all("a", class_="Teaser-link"))
    links.extend(soup.find_all("a", class_="is-hidden"))

    urls = [link["href"] for link in links]
    bookings = [url for url in urls if "index.en.shtml" in url]
    sublocations = [url for url in urls if "index.en.shtml" not in url]

    locations.extend(bookings)
    for sublocation in sublocations:
        traverse(sublocation, session, locations)


def fetch_location(page_url, session):
    response = session.get(page_url, headers=headers)
    if response.status_code != 200:
        return

    loc_dom = etree.HTML(response.text)
    poi = loc_dom.xpath(
        '//script[@type="application/ld+json" and contains(text(), "addressCountry")]/text()'
    )
    if not poi:
        return

    poi = json.loads(poi[0])
    if poi["logo"].split("/")[-1] != "logo_mer.png":
        return

    street_address = loc_dom.xpath('//meta[@property="og:street-address"]/@content')[0]
    latitude = loc_dom.xpath('//meta[@property="og:latitude"]/@content')
    latitude = latitude[0] if latitude else SgRecord.MISSING
    longitude = loc_dom.xpath('//meta[@property="og:longitude"]/@content')
    longitude = longitude[0] if longitude else SgRecord.MISSING

    item = SgRecord(
        locator_domain="accor.com",
        page_url=page_url,
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

    return item


def fetch_data():
    url = "https://all.accor.com/gb/world/hotels-accor-monde.shtml"
    with SgRequests() as session:
        locations = []
        traverse(url, session, locations)

        for location in locations:
            poi = fetch_location(location, session)
            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
