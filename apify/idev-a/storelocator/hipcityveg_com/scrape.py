from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://hipcityveg.com/"
    base_url = "https://hipcityveg.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.locations ul#localtion-list li.store-location")
        for _ in locations:
            addr = list(_.select(".store-info .block")[0].stripped_strings)
            block = list(_.select(".store-info .block")[1].stripped_strings)
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=addr[0],
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                country_code="US",
                phone=block[0],
                hours_of_operation="; ".join(block[1:]),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
