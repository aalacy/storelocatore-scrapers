from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shopsavmor")

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Cookie": "sm_alert=notice",
    "Host": "www.shopsavmor.com",
    "Referer": "https://www.shopsavmor.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.shopsavmor.com/"
    base_url = "https://www.shopsavmor.com/locations.html"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div.location_container > div.location_wrapper")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            block = list(_.select_one("div.location_text").stripped_strings)
            coord = ["", ""]
            try:
                map_tag = _.find("a", href=re.compile(r"https?://maps"))
                coord = map_tag["href"].split("&ll=")[1].split("&s")[0].split(",")
            except:
                try:
                    coord = map_tag["href"].split("&sll=")[1].split("&s")[0].split(",")
                except:
                    pass
            yield SgRecord(
                page_url=base_url,
                store_number=_.select_one("div.location_number")
                .text.strip()
                .split(" ")[-1],
                location_name=_.select_one("div.location_header").text.strip(),
                street_address=block[0],
                city=block[1].split(",")[0].strip(),
                state=block[1].split(",")[1].strip().split(" ")[0].strip(),
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=block[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=block[2],
                locator_domain=locator_domain,
                hours_of_operation=block[3],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
