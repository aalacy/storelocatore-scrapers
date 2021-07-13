from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return [vv.strip() for vv in val if vv.replace("\u200b", "").strip()]


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://sourdoughfuel.com/"
    base_url = "https://www.sourdoughfuelstores.com/store-locator"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select('div#Containercfvg a[data-testid="linkElement"]')
        locations = soup.select('div#Containercfvg div[data-testid="richTextElement"]')[
            1:
        ]
        for x, _ in enumerate(locations):
            block = _valid(list(_.stripped_strings))
            try:
                coord = links[x]["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = links[x]["href"].split("ll=")[1].split("&")[0].split(",")
            hours = "24 hour" if "24" in block[2] else ""
            addr = parse_address_intl(block[1].split(":")[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=block[0].strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                latitude=coord[0],
                longitude=coord[1],
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[-1] if _phone(block[-1]) else "",
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
