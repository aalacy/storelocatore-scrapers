from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("leeversfoods")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.leeversfoods.com/"
base_url = "https://www.leeversfoods.com/StoreLocator/State/?State=ND"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#StoreLocator table tr")[1:]
        logger.info(f"{len(locations)} found")
        for _ in locations:
            td = _.select("td")
            page_url = _.select_one("a.StoreViewLink")["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one("p.Address").stripped_strings)[1:]
            addr = [aa.replace("\xa0", " ") for aa in addr]
            try:
                coord = sp1.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            except:
                coord = ["", ""]
            hours = []
            _hr = sp1.find("dt", string=re.compile(r"Hours of Operation"))
            if _hr:
                hours = _hr.find_next_sibling().text.replace(",", ";")
            yield SgRecord(
                page_url=page_url,
                location_name=td[0].text.strip(),
                street_address=td[1].text.strip(),
                city=td[0].text.strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                latitude=coord[1],
                longitude=coord[0],
                country_code="US",
                phone=td[2].text.strip(),
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("–", "-").replace("•", ";"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
