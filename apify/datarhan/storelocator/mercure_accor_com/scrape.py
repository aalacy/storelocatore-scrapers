import json
from lxml import etree
from urllib.parse import urljoin, urlencode
from requests.sessions import session

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


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


def fetch_data():
    domain = "accor.com"
    start_url = "https://all.accor.com/gb/world/hotels-accor-monde.shtml"
    session = SgRequests()
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_directions = dom.xpath('//div[@class="Teaser Teaser--geography"]//a/@href')
    for url in all_directions:
        all_locations = parse_locations_urls(url)
        for store_url in all_locations:
            store_url = urljoin(start_url, store_url)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            if not loc_dom.xpath('//img[contains(@src, "/mer.svg")]'):
                continue
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


def parse_locations_urls(url):
    all_locations = []
    session = SgRequests()
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    url = urljoin("https://all.accor.com/", url)
    response = session.get(url, headers=hdr)
    code = response.status_code
    while code != 200:
        session = SgRequests()
        response = session.get(url, headers=hdr)
        code = response.status_code
    dom = etree.HTML(response.text)
    urls_to_parse = dom.xpath('//div[@class="Teaser Teaser--geography"]//a/@href')
    urls_to_parse += parse_ids(dom, session)
    for url in urls_to_parse:
        yield url
    all_locations += dom.xpath(
        '//a[@class="Teaser-link" and contains(@href, "/hotel/")]/@href'
    )

    return all_locations


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
