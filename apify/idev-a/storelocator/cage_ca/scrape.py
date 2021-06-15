from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cage.ca/"
    base_url = "https://www.cage.ca/trouver-une-cage"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.search-list li a")
        for link in links:
            page_url = locator_domain + link["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = list(
                soup1.select_one('li:-soup-contains("Adresse:")').stripped_strings
            )
            addr = block[0].split("Adresse:")[-1].split(",")
            map_data = soup1.select_one('li:-soup-contains("Adresse:")').a["href"]
            coord = ["", ""]
            try:
                coord = map_data.split("!1d")[1].split("!2d")
            except:
                try:
                    coord = map_data.split("/@")[1].split("/data")[0].split(",")
                except:
                    pass
            hours = []
            if soup1.select(
                "div.b-store-info__hours table.b-store-info__table__hours tr"
            ):
                for hh in soup1.select("table.b-store-info__table__hours tr")[1:]:
                    td = hh.select("td")
                    if len(td) == 1:
                        break
                    hours.append(f"{td[0].text.strip()}: {td[1].text.strip()}")
            yield SgRecord(
                page_url=page_url,
                location_name=link.text,
                street_address=" ".join(addr[:-2]).strip(),
                city=addr[-2].strip(),
                zip_postal=addr[-1].replace("-", "").strip(),
                latitude=coord[0],
                longitude=coord[1],
                country_code="CA",
                phone=soup1.find("a", href=re.compile(r"tel:")).text,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
