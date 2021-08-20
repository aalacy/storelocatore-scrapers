from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://vuoriclothing.com/"
    base_url = "https://vuoriclothing.com/apps/store-locator/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.store-loc-vuori-store-list div.store-loc-vuori-store"
        )
        for _ in locations:
            addr = list(_.select_one("p.store-loc-vuori-store-addy").stripped_strings)
            block = list(_.select_one("p.store-loc-vuori-store-hours").stripped_strings)
            phone = ""
            if _p(block[-1]):
                phone = block[-1]
                del block[-1]
            street_address = " ".join(addr[:-1]).strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=base_url,
                location_name=_.select_one("p.store-loc-vuori-store-name").text,
                street_address=street_address,
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                locator_domain=locator_domain,
                phone=phone,
                hours_of_operation="; ".join(block).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
