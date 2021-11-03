from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.acmestores.com/"
    base_url = "https://www.acmestores.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        hours_title = soup.find("p", string=re.compile(r"stores", re.IGNORECASE))
        hours_of_operation = hours_title.find_next_sibling("p").text
        locations = soup.select("table.table-striped tbody tr")
        for _ in locations:
            td = _.select("td")
            addr = parse_address_intl(td[1].text)
            try:
                coord = td[1].a["href"].split("ll=")[1].split("&s")[0].split(",")
            except:
                try:
                    coord = td[1].a["href"].split("/@")[1].split("z/data")[0].split(",")
                except:
                    coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=td[0].text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=addr.postcode,
                country_code="US",
                phone=td[2].text,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
