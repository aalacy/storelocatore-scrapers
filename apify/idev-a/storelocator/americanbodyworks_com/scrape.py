from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup
import re

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

logger = SgLogSetup().get_logger("americanbodyworks_com")


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def _phone(soup1):
    phone = ""
    for tag in [
        aa
        for aa in soup1.select_one(
            "aside div.widget.widget_text div.textwidget"
        ).stripped_strings
    ]:
        if re.search(r"phone:", tag, re.IGNORECASE):
            phone = tag.replace("Phone:", "").strip()
    return phone


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://americanbodyworks.com/"
        base_url = "https://americanbodyworks.com/"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.second.bellow_header ul li")
        for link in links:
            page_url = link.a["href"]
            store_number = link["id"].split("-")[-1]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _address = soup1.select_one("div.widget.widget_text h5").text
            addr = parse_address_intl(_address)
            logger.info(page_url)
            yield SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=link.a.span.text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_phone(soup1),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
