from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    locator_domain = "https://www.powerfinancetexas.com"
    base_url = "https://www.powerfinancetexas.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select_one("h3.widget-title").find_next_sibling("div").select("a")
        for link in links:
            soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            dir_h4 = soup1.find("h4", string=re.compile(r"direction", re.IGNORECASE))
            addr = list(dir_h4.find_next_sibling("p").stripped_strings)
            state_zip = addr[1].split(",")[1].strip().split(" ")
            coord = soup1.iframe["src"].split("!2d")[1].split("!3m")[0].split("!3d")
            hours = []
            for hh in soup1.select("table tr"):
                hours.append(
                    f"{hh.select('td')[0].text.strip()}: {hh.select('td')[1].text.strip()}"
                )
            yield SgRecord(
                page_url=link["href"],
                location_name=soup1.h1.text,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=state_zip[0],
                zip_postal=state_zip[-1],
                phone=addr[-1],
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
