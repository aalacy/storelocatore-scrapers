from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.leeversfoods.com/"
    base_url = "https://www.leeversfoods.com/store-locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("main div.flex_column.av_one_fourth a.avia-button")
        for link in links:
            sp1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            addr = list(sp1.select_one("section.av_textblock_section").stripped_strings)
            _phone = sp1.find("h3", string=re.compile(r"Phone:"))
            phone = _phone.text.split(":")[-1] if _phone else ""
            try:
                coord = sp1.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            except:
                coord = ["", ""]
            hours = []
            _hr = sp1.find("h2", string=re.compile(r"Hours:"))
            if _hr:
                hours = list(_hr.find_next_sibling().stripped_strings)
            yield SgRecord(
                page_url=link["href"],
                location_name=sp1.select_one('h2[itemprop="headline"]').text,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                latitude=coord[1],
                longitude=coord[0],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
