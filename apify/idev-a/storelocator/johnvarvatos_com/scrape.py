from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from lxml import etree

logger = SgLogSetup().get_logger("johnvarvatos")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.johnvarvatos.com"
base_url = "https://www.johnvarvatos.com/stores"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.storelocator-result div.store")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link.h2.a["href"]
            logger.info(page_url)
            sp1 = etree.HTML(session.get(page_url, headers=_headers).text)
            addr = link["data-store-address"].split(",")
            hours = []
            if sp1.xpath('//div[@class="storedetails-hours"]//text()'):
                hours = [
                    hh.strip()
                    for hh in sp1.xpath('//div[@class="storedetails-hours"]//text()')
                    if hh.strip()
                ][1:]

            phone = ""
            if link.select_one("span.store-phone-number"):
                phone = link.select_one("span.store-phone-number").text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=link.h2.a["id"],
                location_name=link.h2.text.strip(),
                street_address=" ".join(addr[:-3]),
                city=addr[-3].strip(),
                state=addr[-2].strip(),
                zip_postal=addr[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link["data-lat"],
                longitude=link["data-lng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=link["data-store-address"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
