from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("baartprograms")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    locator_domain = "https://baartprograms.com/"
    base_url = "https://baartprograms.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.fl-module-dual-color-heading")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            try:
                coord = (
                    sp1.select_one("div.fl-node-content iframe")["src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")[::-1]
                )
            except:
                coord = ["", ""]
            addr = list(
                sp1.find("h3", string=re.compile(r"^Contact Information"))
                .find_parent()
                .find_next_sibling()
                .p.stripped_strings
            )
            block = list(
                sp1.find("h3", string=re.compile(r"^Contact Information"))
                .find_parent()
                .find_next_sibling()
                .select("p")[1]
                .stripped_strings
            )
            hours = []
            _hr = sp1.find("h3", string=re.compile(r"Operating Hours"))
            if _hr:
                temp = []
                for hh in _hr.find_parent().find_next_sibling().select("p"):
                    temp += list(hh.stripped_strings)
                _day = []
                _hour = []
                for x, hh in enumerate(temp):
                    if (
                        hh.split("-")[0]
                        .split("–")[0]
                        .split(":")[0]
                        .split("&")[0]
                        .strip()
                        in days
                    ):
                        if _day and _hour:
                            hours.append(f"{''.join(_day)}: {' '.join(_hour)}")
                            _day = []
                        if hh.endswith(":"):
                            hh = hh[:-1]
                        _day.append(hh)
                        _hour = []
                    elif "holiday" not in hh.lower():
                        _hour.append(hh)

                    if x == len(temp) - 1 or hh.lower().startswith("holiday"):
                        hours.append(f"{''.join(_day)}: {' '.join(_hour)}")
                    if hh.lower().startswith("holiday"):
                        break
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("h1.fl-heading").text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=block[1],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
