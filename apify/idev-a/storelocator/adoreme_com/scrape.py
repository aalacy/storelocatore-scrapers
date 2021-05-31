from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from datetime import datetime
from sgselenium import SgChrome

logger = SgLogSetup().get_logger("adoreme")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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
    locator_domain = "https://www.adoreme.com/"
    base_url = "https://www.stores.adoreme.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = [
            link
            for link in soup.select("main div.col.sqs-col-5.span-5 .sqs-block")
            if "spacer-block" not in link["class"]
        ]
        logger.info(f"{len(links)} found")
        with SgChrome() as driver:
            for x in range(0, len(links), 3):
                link = links[x + 2]
                name = " ".join(
                    re.findall("[A-Z][^A-Z]*", links[x].img["alt"].split("_")[0])
                )
                addr = link.a.text.split(",")
                _hr = link.find(
                    "strong", string=re.compile(r"store hours:", re.IGNORECASE)
                )
                phone = ""
                if _p(_hr.find_parent().find_previous_sibling().text):
                    phone = _hr.find_parent().find_previous_sibling().text
                page_url = link.find_all("a")[-1]["href"]
                logger.info(page_url)
                driver.get(page_url)
                sp1 = bs(driver.page_source, "lxml")
                hours = []
                if sp1.select("div.visit-hours ul li"):
                    for hh in sp1.select("div.visit-hours ul li"):
                        _hr = list(hh.stripped_strings)
                        if _hr[0] == "We're Open:":
                            _hr[0] = days[datetime.today().weekday()]
                        _hr[0] = _hr[0].split(",")[0]
                        hours.append(": ".join(_hr))
                elif sp1.select("table.mabel-bhi-businesshours tr"):
                    hours = [
                        ":".join(hh.stripped_strings)
                        for hh in sp1.select("table.mabel-bhi-businesshours tr")
                    ]
                elif sp1.select_one('button[data-child="hoo"]'):
                    hours = list(
                        sp1.select_one('button[data-child="hoo"]').stripped_strings
                    )
                try:
                    coord = link.a["href"].split("/@")[1].split("/data")[0].split(",")
                except:
                    coord = ["", ""]
                yield SgRecord(
                    page_url=page_url,
                    location_name=name,
                    street_address=addr[0],
                    city=addr[1],
                    state=addr[2].strip().split(" ")[0].strip(),
                    zip_postal=addr[2].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
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
