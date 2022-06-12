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
        .replace("’", "'")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    locator_domain = "https://www.indigourgentcare.com"
    base_url = "https://www.indigourgentcare.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.location-listing li")
        for _ in locations:
            page_url = locator_domain + _["data-url"]
            addr = list(_.address.stripped_strings)
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hour_block = soup1.find("h6", string=re.compile(r"Hours"))
            hours = []
            for hh in hour_block.next_siblings:
                if not hh.string:
                    continue
                hours.append(hh.string.strip())
            street_address = addr[0]
            if len(addr) > 2:
                street_address = " ".join(addr[:-1])
            yield SgRecord(
                page_url=page_url,
                location_name=_["data-title"],
                street_address=street_address,
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                phone=_.find("a", href=re.compile(r"tel:")).text,
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
