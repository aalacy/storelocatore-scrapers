from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from datetime import datetime
from sgselenium import SgChrome
import ssl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("adoreme")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
locator_domain = "https://www.adoreme.com/"
base_url = "https://www.stores.adoreme.com/"


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
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = [
            link
            for link in soup.select("main div.col.sqs-col-5.span-5 .sqs-block")
            if "spacer-block" not in link["class"]
        ]
        logger.info(f"{len(links)/3} found")
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
                if not phone:
                    _phone = sp1.find("a", href=re.compile(r"tel:"))
                    if _phone:
                        phone = _phone.text.strip()
                hours = []
                if sp1.select("div.visit-hours ul li"):
                    for hh in sp1.select_one("div.visit-hours").select("ul li"):
                        _hr = list(hh.stripped_strings)
                        _hr[0] = _hr[0].split(",")[0]
                        if (
                            _hr[0] == "We're Open:"
                            or _hr[0] not in days
                            or _hr[0] == "Today's Hours:"
                        ):
                            _hr[0] = days[datetime.today().weekday()]
                        hours.append(": ".join(_hr))
                    if not phone:
                        phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
                elif sp1.select("div.weeklyHours dl"):
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in sp1.select("div.weeklyHours dl")
                    ]
                elif sp1.select("table.mabel-bhi-businesshours tr"):
                    temp = [
                        ":".join(hh.stripped_strings)
                        for hh in sp1.select("table.mabel-bhi-businesshours")[0].select(
                            "tr"
                        )
                    ]
                    for hh in temp:
                        if hh[:3] not in days:
                            break
                        hours.append(hh)
                elif sp1.select("article.cblHeaderTbl--dates dl"):
                    hours = [
                        ":".join(hh.stripped_strings)
                        for hh in sp1.select("article.cblHeaderTbl--dates dl")
                        if "hours" not in hh.text
                    ]
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
                    hours_of_operation="; ".join(hours)
                    .replace("–", "-")
                    .replace("—", "-"),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
