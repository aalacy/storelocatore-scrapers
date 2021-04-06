from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.bridgehead.ca"
    base_url = "https://www.bridgehead.ca/pages/coffeehouses"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = dirtyjson.loads(
            res.split("var sites = ")[1]
            .strip()
            .split("function setMarkers")[0]
            .strip()[:-1]
            .replace("\n", "")
            .replace("\t", "")
        )
        for _ in locations:
            mymap = bs(_[4], "lxml")
            block = list(mymap.stripped_strings)
            page_url = locator_domain + mymap.a["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(soup1.select_one("div.page__content.rte p").stripped_strings)
            if "Fax" in addr[-1]:
                del addr[-1]
            state_zip = (
                addr[-3]
                .split(",")[1]
                .strip()
                .replace("&nbsp;", " ")
                .replace("\xa0", " ")
            )
            state_zip = state_zip.split(" ")

            yield SgRecord(
                page_url=page_url,
                location_name=_[0],
                street_address=" ".join(addr[:-3]).replace("\xa0", " "),
                city=addr[-3].split(",")[0],
                state=state_zip[0],
                zip_postal=" ".join(state_zip[1:]),
                country_code="CA",
                latitude=_[1],
                longitude=_[2],
                phone=addr[-1],
                locator_domain=locator_domain,
                hours_of_operation=block[-2],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
