from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("hcrcenters")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.hcrcenters.com"
base_url = "https://www.hcrcenters.com/our-location/"


def _p(val):
    if (
        val
        and val.split(":")[-1]
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val.split(":")[-1]
    else:
        return ""


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            sp0 = bs(session.get(base_url, headers=_headers).text, "lxml")
            data_url = sp0.select_one("div.bitmap script")["src"]
            driver.get(data_url)
            links = json.loads(
                bs(driver.page_source, "lxml")
                .text.split(".maps(")[1]
                .split(").data(")[0]
            )["places"]
            logger.info(f"{len(links)} found")
            for link in links:
                loc = link["location"]
                block = list(bs(link["content"], "lxml").stripped_strings)
                if "\n" in block[0]:
                    bb = block[0].split("\n")
                else:
                    bb = block
                page_url = bs(link["content"], "lxml").a["href"]
                if not page_url.startswith("http"):
                    page_url = locator_domain + page_url
                logger.info(page_url)
                res = session.get(page_url, headers=_headers)
                if res.status_code == 200:
                    sp1 = bs(res.text, "lxml")
                    hours = []
                    if sp1.select_one("div.sidebar-info-time"):
                        temp = list(
                            sp1.select_one("div.sidebar-info-time").stripped_strings
                        )
                        for hh in temp[1:]:
                            if "treatment center hours" in hh.lower():
                                continue
                            if "medication hours" in hh.lower():
                                break
                            hours.append(hh)
                    elif sp1.find("h3", string=re.compile(r"Operating Hours")):
                        hours = list(
                            sp1.find("h3", string=re.compile(r"Operating Hours"))
                            .find_parent()
                            .find_next_sibling()
                            .stripped_strings
                        )
                    elif sp1.select("div.treatment-work"):
                        hours = [
                            " ".join(hh.stripped_strings)
                            for hh in sp1.select_one("div.treatment-work").select(
                                "div.tw-item"
                            )
                        ]
                    elif sp1.find("span", string=re.compile(r"^OPERATING HOURS$")):
                        hr = sp1.find(
                            "span", string=re.compile(r"^OPERATING HOURS$")
                        ).find_parent("p")
                        hours = [
                            hh.text.strip()
                            for hh in hr.find_next_siblings("p")
                            if hh.text.strip()
                        ]
                    phone = ""
                    if sp1.find("a", href=re.compile(r"tel:")):
                        phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
                else:
                    phone = bb[2].replace("|", "").strip()

                yield SgRecord(
                    page_url=page_url,
                    location_name=link["title"],
                    street_address=bb[0].strip(),
                    city=loc["city"],
                    state=loc["state"],
                    zip_postal=loc["postal_code"],
                    country_code="US",
                    phone=_p(phone),
                    locator_domain=locator_domain,
                    latitude=loc["lat"],
                    longitude=loc["lng"],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
