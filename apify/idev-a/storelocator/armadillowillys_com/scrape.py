from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
import bs4

logger = SgLogSetup().get_logger("armadillowillys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://www.armadillowillys.com/"
    base_url = "http://www.armadillowillys.com/locations.asp"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("table#locations tr")
        _hr = soup.find("img", src=re.compile(r"title_hours"))
        temp = []
        hours = []
        for hh in _hr.next_siblings:
            if isinstance(hh, bs4.element.NavigableString):
                if not hh.strip():
                    continue
                if "Looking for" in hh.strip():
                    break
                temp.append(hh.strip())
            if isinstance(hh, bs4.element.Tag):
                if not hh.text.strip():
                    continue
                temp.append(hh.text.strip())
        if temp[-1] == "Click here":
            del temp[-1]
        for x in range(0, len(temp), 2):
            hours.append(f"{temp[x]} {temp[x+1]}")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            logger.info(page_url)
            coord = ["", ""]
            res = session.get(page_url, headers=_headers)
            addr = list(_.select_one("td.address").stripped_strings)
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                try:
                    coord = (
                        sp1.select_one("div iframe")["src"]
                        .split("!2d")[1]
                        .split("!2m")[0]
                        .split("!3d")
                    )
                except:
                    coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=addr[1],
                street_address=addr[0],
                city=addr[1],
                state=addr[2].split(" ")[1].strip(),
                zip_postal=addr[2].split(" ")[-1].strip(),
                country_code="US",
                phone=_.select_one("td.phone").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
