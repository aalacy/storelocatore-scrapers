from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("cjlogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cjlogistics.com"
base_url = "https://www.cjlogistics.com/en/network/country"


def _p(val):
    _val = (
        val.lower()
        .split("|")[0]
        .split("fax")[0]
        .split(":")[-1]
        .split("/")[0]
        .replace("(call center)", "")
        .strip()
    )
    if (
        _val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return _val
    else:
        return ""


def _d(link, _addr, page_url, location_name="", latitude="", longitude=""):
    phone = ""
    if link.select_one("span.phone"):
        phone = link.select_one("span.phone").text.strip()
    addr = parse_address_intl(_addr)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return SgRecord(
        page_url=page_url,
        street_address=street_address,
        location_name=location_name,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code=link.a.text.split("(")[0].strip(),
        phone=_p(phone),
        locator_domain=locator_domain,
        latitude=latitude,
        longitude=longitude,
        raw_address=_addr,
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.country-list li")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.select("a")[-1]["href"]
            if not page_url.startswith("http"):
                page_url = locator_domain + page_url
            if link.a.get("onclick"):
                _id = link.a["onclick"].split("fnOfficeListPop('")[1].split("'")[0]
                url = f"https://www.cjlogistics.com/en/network/office-list?countryId={_id}&_=1623096569356"
                logger.info(url)
                locations = session.get(url, headers=_headers).json()["result"]
                logger.info(f"[{len(locations)}]")
                for _ in locations:
                    yield _d(
                        link,
                        _["address"],
                        page_url,
                        _["corperationName"],
                        _["latitude"],
                        _["longitude"],
                    )
            else:
                yield _d(link, link.p.text, page_url)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
