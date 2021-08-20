from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("’", "'")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    locator_domain = "https://russmarket.com/"
    base_url = "https://russmarket.com/connect/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.theme-content div.js-master-row")
        for _ in locations:
            if len(_.find_all("div", class_="column_container")) < 2:
                continue

            main = list(_.select("div.column_container")[1].p.stripped_strings)
            coord = (
                _.select("div.column_container")[0]
                .iframe["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!3d")
            )
            phone = main[2]
            address = main[0]
            if re.search(r"phone", phone, re.IGNORECASE):
                phone = main[3]
                address = " ".join(main[:2])
            addr = parse_address_intl(address)
            yield SgRecord(
                page_url=base_url,
                location_name=_valid(_.select("div.column_container")[1].h3.text),
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
