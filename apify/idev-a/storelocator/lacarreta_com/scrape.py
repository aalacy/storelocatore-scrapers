from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("“", '"')
        .replace("”", '"')
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    locator_domain = "http://lacarreta.com/"
    base_url = "http://lacarreta.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#loc-container div.location.item")
        for _ in locations:
            addr = list(_.select("p")[0].stripped_strings)
            hours = list(_.select("p")[2].stripped_strings)
            for x, hour in enumerate(hours):
                if re.search(r"hour", hour, re.IGNORECASE):
                    del hours[x]

            zip_postal = ""
            try:
                zip_postal = addr[1].split(",")[1].strip().split(" ")[1]
            except:
                pass
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=_valid(addr[0]),
                city=addr[1].split(",")[0],
                state=addr[1].split(",")[1].strip().split(" ")[0],
                zip_postal=zip_postal,
                country_code="US",
                phone=_.select("p")[1].text,
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
