# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import re

from bs4 import BeautifulSoup

from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.christiedental.com/"
    domain = "christiedental.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="office-card"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//h3[@class="office-card__title"]/text()')[0]
        page_url = poi_html.xpath('.//a[@class="office-card__website"]/@href')[0]
        if "cdofocalacentral" in page_url:
            page_url = page_url.replace("https", "http")
        loc_response = session.get(page_url)
        base = BeautifulSoup(loc_response.text, "lxml")

        raw_address = poi_html.xpath('.//div[@class="office-card__address"]/div/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        phone = poi_html.xpath('.//a[@class="office-card__phone"]/text()')[0].strip()
        store_number = re.findall('hdcid: "(.+?)",', loc_response.text)[0]
        hours = " ".join(list(base.find(class_="days").stripped_strings))
        latitude = re.findall(r'latitude: "(.+?)",', loc_response.text)[0]
        longitude = re.findall('longitude: "(.+?)",', loc_response.text)[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0].split(" 775 E")[0].replace(" ,", ","),
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=raw_address[1].split(", ")[-1].split()[-1],
            country_code="US",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours,
        )

        yield item


def scrape():
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
