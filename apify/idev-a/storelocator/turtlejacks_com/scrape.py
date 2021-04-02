from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("–", "-").strip()


def fetch_data():
    locator_domain = "https://turtlejacks.com/"
    base_url = "https://turtlejacks.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#location_container div.location_wrapper")
        for _ in locations:
            addr = list(_.select("p")[0].stripped_strings)[-1].split(",")
            yield SgRecord(
                page_url=_.h3.a["href"],
                location_name=_.h3.text,
                street_address=addr[0],
                city=addr[1],
                state=addr[2],
                country_code="CA",
                phone=_.select_one("p.reservations a").text,
                locator_domain=locator_domain,
                hours_of_operation=_valid(
                    "; ".join(list(_.select_one("div.hours").stripped_strings)[1:])
                ),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
