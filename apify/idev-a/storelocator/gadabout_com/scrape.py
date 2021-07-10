from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _phone(temp, addr):
    phone = ""
    for tt in temp:
        block = list(tt.stripped_strings)
        if len(block) < 2:
            continue
        if (
            addr.postcode in " ".join(block)
            and addr.state in " ".join(block)
            and addr.street_address_1.split(" ")[0] in " ".join(block)
        ):
            phone = block[-2]
            break
    return phone


def fetch_data():
    locator_domain = "https://gadabout.com/"
    base_url = "https://gadabout.com/pages/locations"
    json_url = "https://www.powr.io/cached/19912276.json"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        temp = soup.select(
            "div.shg-box-vertical-align-wrapper .shg-c div.shg-row div.shg-rich-text"
        )[1:]
        locations = session.get(json_url, headers=_headers).json()["content"][
            "locations"
        ]
        hours = []
        for hh in soup.select("div#footer div")[0].select("p"):
            if hh.text.strip():
                hours.append(hh.text.strip())
        for _ in locations:
            addr = parse_address_intl(_["address"])
            yield SgRecord(
                page_url=base_url,
                location_name=bs(_["name"], "lxml").text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=addr.postcode,
                country_code="US",
                phone=_phone(temp, addr),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
