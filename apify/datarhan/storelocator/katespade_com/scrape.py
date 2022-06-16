from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "katespade.com"
    start_url = "https://www.katespade.com/stores/index.html"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = []
    countries = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for url in countries:
        country_url = urljoin(start_url, url)
        response = session.get(country_url)
        dom = etree.HTML(response.text)
        all_states = dom.xpath('//a[@class="Directory-listLink"]')
        for state in all_states:
            state_url = urljoin(country_url, state.xpath("@href")[0])
            count = state.xpath("@data-count")[0][1:-1]
            if count == "1":
                all_locations.append(state_url)
                continue
            response = session.get(urljoin(country_url, state_url))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[span[@class="LocationName"]]/@href')
            all_locations += dom.xpath('//a[@data-ya-track="businessname"]/@href')
            cities = dom.xpath('//a[@class="Directory-listLink"]')
            for city in cities:
                url = city.xpath("@href")[0]
                count = city.xpath("@data-count")[0][1:-1]
                if count == "1":
                    all_locations.append(url)
                    continue
                response = session.get(urljoin(state_url, url))
                dom = etree.HTML(response.text)
                all_locations += dom.xpath('//a[span[@class="LocationName"]]/@href')
                all_locations += dom.xpath('//a[@data-ya-track="businessname"]/@href')

    for url in list(set(all_locations)):
        if "https" not in url:
            if url.startswith(".."):
                url = url[2:]
            page_url = "https://www.katespade.com/stores" + url
        else:
            page_url = url
        page_url = page_url.replace("/../", "/")
        if "1000-premium-outlets-drive-1871" in page_url:
            continue
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = "".join(loc_dom.xpath('//h1[@itemprop="name"]//text()'))
        if "STORE CLOSED" in location_name:
            continue
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = street_address[0]
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = loc_dom.xpath("//address/@data-country")[0]
        phone = loc_dom.xpath('//div[@id="phone-main"]/text()')[0]
        location_type = ""
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath('//table[@class="c-hours-details"]//text()')[2:]
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
