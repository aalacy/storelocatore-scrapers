from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://sealmaster.net"
base_url = "https://sealmaster.net/locations/"


def _phone(val):
    return (
        val.replace("SEAL", "")
        .replace("(", "")
        .replace("Phone:", "")
        .replace("Phone", "")
        .replace(")", "")
        .replace("-", "")
        .replace("+", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def _d(_, country_code=""):
    page_url = base_url
    if _.select("h4 a"):
        page_url = locator_domain + _.select("h4 a")[-1]["href"]
    if not _.p:
        return None
    addr = list(_.p.stripped_strings)
    if len(addr) == 1 and not _phone(addr[0]):
        addr = list(_.select("p")[1].stripped_strings)
    if addr[-1] == "MAP":
        del addr[-1]
    if "WEBSITE" in addr[-1]:
        del addr[-1]
    if "Contact" in addr[-1]:
        del addr[-1]
    if "Fax" in addr[-1]:
        del addr[-1]
    phone = ""
    street_address = city = state = zip_postal = ""
    if not country_code:
        if len(_.select("h4")) == 2:
            country_code = _.h4.text.strip()
        else:
            country_code = _.find_parent("div").h4.text.strip()
    if len(addr) > 1:
        if "Licensed Manufacturer" in addr[0]:
            del addr[0]
        if "km" in addr[1]:
            del addr[1]

        if _phone(addr[-1]):
            phone = addr[-1]
            del addr[-1]
        if _phone(addr[-1]):
            phone = addr[-1]
            del addr[-1]

        _addr = parse_address_intl(" ".join(addr))
        street_address = _addr.street_address_1
        if _addr.street_address_2:
            street_address += " " + _addr.street_address_2
        street_address = street_address
        city = _addr.city
        state = _addr.state
        zip_postal = _addr.postcode
        if _addr.country:
            country_code = _addr.country
        if zip_postal.startswith("C.P "):
            country_code = "MEXICO"
    else:
        phone = addr[0]
    coord = ["", ""]
    if _.p.a:
        try:
            coord = _.p.a["href"].split("/@")[1].split("z/data")[0].split(",")
        except:
            pass
    return SgRecord(
        page_url=page_url,
        location_name=_.select("h4")[-1].text,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        latitude=coord[0],
        longitude=coord[1],
        country_code=country_code.replace("Sealcoat", "US"),
        phone=phone.replace("Phone:", ""),
        locator_domain=locator_domain,
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div#av_section_2 div.entry-content-wrapper section.av_textblock_section"
        )
        for _ in locations:
            yield _d(_, "US")
        locations = soup.select(
            "div#av_section_3 div.entry-content-wrapper section.av_textblock_section"
        )
        for _ in locations:
            yield _d(_)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
