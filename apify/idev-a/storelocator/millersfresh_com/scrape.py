from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("millersfresh")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://www.millersfresh.com/",
    "cookie": "fp-session=%7B%22token%22%3A%225cca8ac349ed0cfc22db523c82c47ead%22%7D; fp-pref=%7B%7D; _ga=GA1.2.1010189863.1619217025; _gid=GA1.2.533249316.1619217025; fp-history=%7B%220%22%3A%7B%22name%22%3A%22%2Fstore-locations%2F%22%7D%2C%221%22%3A%7B%22name%22%3A%22%2Fstore-locations%2Fcooperstown%2F%22%7D%7D",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.millersfresh.com/"
    base_url = "https://www.millersfresh.com/store-locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.entry-content-wrapper .flex_column a.avia-button")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one(".avia_textblock").stripped_strings)
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select(
                    "div#av-layout-grid-2 div.avia-builder-el-last ul li"
                )
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one('h2[itemprop="headline"]').text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=sp1.select(".avia_textblock")[1].text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
