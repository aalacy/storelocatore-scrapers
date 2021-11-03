from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from lxml import etree
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("kirklands")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "kirklands.com"
base_url = "https://www.kirklands.com/custserv/locate_store.cmd?icid=hlink6b_ao_store+locator_N"


def fetch_data():
    with SgRequests() as session:
        response = session.get(base_url, headers=_headers)
        links = etree.HTML(response.text).xpath('//div[@id="stateListing"]//a/@href')
        logger.info(f"{len(links)} found")
        for url in links:
            store_url = urljoin("https://www.kirklands.com", url)
            location_response = session.get(store_url)
            if location_response.status_code != 200:
                continue
            location_dom = etree.HTML(location_response.text)
            sp1 = bs(location_response.text, "lxml")
            if location_dom.xpath('//div[@class="sectionHero"]/img'):
                continue
            logger.info(store_url)
            location_name = location_dom.xpath('//h1[@itemprop="name"]/text()')
            location_name = location_name[0] if location_name else ""
            street_address = location_dom.xpath(
                '//span[@itemprop="streetAddress"]/text()'
            )
            street_address = street_address[0].strip() if street_address else ""
            city = location_dom.xpath('//span[@itemprop="addressLocality"]/text()')[-1]
            city = city if city else ""
            state = location_dom.xpath('//span[@itemprop="addressRegion"]/text()')
            state = state[0].strip() if state else ""
            zip_code = location_dom.xpath('//span[@itemprop="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else ""
            phone = location_dom.xpath('//a[@itemprop="telephone"]/u/text()')
            phone = phone[0] if phone else ""
            latitude = location_dom.xpath('//meta[@itemprop="latitude"]/@content')
            latitude = latitude[0] if latitude else ""
            longitude = location_dom.xpath('//meta[@itemprop="longitude"]/@content')
            longitude = longitude[0] if longitude else ""
            hours_of_operation = "; ".join(
                [": ".join(hh.stripped_strings) for hh in sp1.select("table.hours tr")]
            )
            yield SgRecord(
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
