from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://provinos.com/"
    base_url = "https://provinos.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.fusion-layout-column.fusion_builder_column_1_3")
        for _ in locations:
            block = _.select("p")
            if "Now also offering" in block[0].text:
                del block[0]
            addr = list(block[0].stripped_strings)
            hours = []
            for hh in list(block[1].stripped_strings)[3:]:
                if "Manager" in hh:
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=_.h2.a["href"],
                location_name=_.h2.a.text.strip().replace("’", "'"),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                phone=addr[-1],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
