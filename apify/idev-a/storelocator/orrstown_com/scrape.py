from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("orrstown")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://www.orrstown.com/"
    base_url = "https://www.orrstown.com/find-us"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.officeLocation ")
        logger.info(f"{len(links)} found")
        for link in links:
            _hr = link.find("h6", string=re.compile(r"Hours"))
            addr = list(_hr.find_previous_sibling().stripped_strings)
            phone = ""
            if _p("".join(addr)):
                phone = "".join(addr)
                addr = list(
                    _hr.find_previous_sibling().find_previous_sibling().stripped_strings
                )
            hours = []
            if _hr:
                hours = list(_hr.find_next_sibling().stripped_strings)
                if hours == ["By appointment only"]:
                    hours = []
            try:
                coord = (
                    link.iframe["src"]
                    .split("!2d")[1]
                    .split("!3m")[0]
                    .split("!2m")[0]
                    .split("!3d")
                )
            except:
                coord = ["", ""]
            location_type = "branch"
            if link.select("p.big")[-1].text.strip() != "No ATM":
                location_type += ",atm"
            yield SgRecord(
                page_url=base_url,
                location_name="".join(link.h2.stripped_strings),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                phone=phone,
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
