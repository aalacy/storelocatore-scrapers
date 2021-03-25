from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    base_url = "https://www.omahasteaks.com/servlet/OnlineShopping?Dsp=2408"
    locator_domain = "https://www.omahasteaks.com/"

    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.vlinks a.storelink")
        for link in links:
            soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            phone = soup1.select_one("a.phonelink").text
            addr = list(soup1.select_one("div.ckogroup.no_topborder").stripped_strings)
            hours = soup1.find(
                "", string=re.compile(r"Almost all stores", re.IGNORECASE)
            )
            yield SgRecord(
                page_url=link["href"],
                store_number=link["href"].split("&storeid=")[1].split("&")[0],
                location_name=link.text.strip(),
                street_address=addr[-3].replace("\n", "").replace("\t", ""),
                city=addr[-2].split(",")[0].strip(),
                state=addr[-2].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-2].split(",")[1].strip().split(" ")[1].strip(),
                phone=phone,
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=hours.replace(
                    "Almost all stores are now operating", ""
                ).strip(),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
