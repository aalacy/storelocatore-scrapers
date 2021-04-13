from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://shopsmartfoods.com"
    base_url = (
        "https://shopsmartfoods.com/StoreLocator/Search/?ZipCode=95453&miles=1000"
    )
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#StoreLocator tr a")
        for link in links:
            addr = list(link.stripped_strings)
            state_zip = " ".join(addr[3:]).strip().split(" ")
            page_url = link["href"].replace("&amp;", "&")
            sp1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text
            else:
                continue

            yield SgRecord(
                page_url=page_url,
                location_name=addr[0],
                street_address=addr[1],
                city=addr[2],
                state=state_zip[1].strip(),
                zip_postal=state_zip[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
