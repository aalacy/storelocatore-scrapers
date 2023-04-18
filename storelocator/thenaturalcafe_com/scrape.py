from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _addr(addr):
    street_address = " ".join(addr[:-1]).strip()
    zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
    city = addr[-1].split(",")[0].strip()
    state = addr[-1].split(",")[1].strip().split(" ")[0].strip()

    return street_address, city, state, zip_postal


def _phone(soup, street, state):
    phone = ""
    for _ in soup.select("div.site-footer-widgets aside"):
        data = list(_.select_one("div.textwidget").stripped_strings)
        if "@" in data[-1]:
            del data[-1]
        _street_address, _city, _state, _zip_postal = _addr(data[:-1])
        if state == _state and street.split(" ")[0] in _street_address:
            phone = data[-1]
            break

    return phone


def fetch_data():
    locator_domain = "https://thenaturalcafe.com/"
    base_url = "https://thenaturalcafe.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        h2_block = soup.select("div.entry-content h2")
        for _ in h2_block:
            siblings = [si for si in _.find_next_siblings("p") if si.text]
            addr = list(siblings[0].stripped_strings)
            coord = (
                _.find_next_sibling("iframe")["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!2m")[0]
                .split("!3d")
            )
            street_address, city, state, zip_postal = _addr(addr)
            yield SgRecord(
                page_url=base_url,
                location_name=_.text,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=coord[1],
                longitude=coord[0],
                country_code="US",
                phone=_phone(soup, street_address, state),
                hours_of_operation=siblings[1].text.replace("Hours", "").strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
