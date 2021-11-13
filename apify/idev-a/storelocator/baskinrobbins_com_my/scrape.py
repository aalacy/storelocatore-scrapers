from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.baskinrobbins.com.my"
base_url = "https://www.baskinrobbins.com.my/content/baskinrobbins/en/location.html"


def _cz(val):
    return val.split()[0].strip(), " ".join(val.split()[1:]).strip()


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul#myUL li")
        for _ in locations:
            raw_address = (
                _.h5.find_next_sibling("p")
                .text.replace("\n", " ")
                .replace("\r", "")
                .strip()
            )
            raw_address = " ".join(
                [aa.strip() for aa in raw_address.split() if aa.strip()]
            )
            state = zip_postal = city = street_address = ""
            addr = parse_address_intl(raw_address + ", Malaysia")
            zip_postal = addr.postcode
            if zip_postal and zip_postal.isdigit():
                city = addr.city
                state = addr.state
            else:
                addr = raw_address.split(",")
                if addr[-1].split()[0].isdigit():
                    zip_postal, city = _cz(addr[-1])
                elif addr[-2].split()[0].isdigit():
                    state = addr[-1].strip()
                    zip_postal, city = _cz(addr[-2])
                else:
                    state = addr[-1].strip()
                    zip_postal, city = _cz(addr[-3])
            if state:
                if "Johor Bahru" in state:
                    city = "Johor Bahru"
                    state = "Johor"
                elif "Johor" in state:
                    state = "Johor"
            street_address = raw_address.split(zip_postal)[0].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            _p = list(_.select_one("p.availability").stripped_strings)
            if _p[0] != "Tel:":
                del _p[0]
            phone = _p[1]
            if phone == "N/A":
                phone = ""
            yield SgRecord(
                page_url=base_url,
                location_name=list(_.h5.stripped_strings)[0],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="MY",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
