from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("blindstogo")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://www.blindstogo.com"
    base_url = "https://www.blindstogo.com/programs/store-finder/stores.xml"
    with SgRequests(proxy_rotation_failure_threshold=10) as session:
        links = bs(session.get(base_url, headers=_headers).text, "lxml").select("store")
        logger.info(f"{len(links)} found")
        for link in links:
            session = SgRequests(proxy_rotation_failure_threshold=10)
            page_url = link.storeurl.text
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            if (
                sp1.select_one("h1.sppb-title-heading")
                and "Coming Soon!" in sp1.select_one("h1.sppb-title-heading").text
            ):
                continue
            if sp1.h1 and sp1.h1.text.strip().startswith("WE’VE MOVED TO"):
                page_url = (
                    locator_domain
                    + sp1.select_one(
                        "div.sppb-addon-content a.sppb-btn-success.sppb-btn-lg"
                    )["href"]
                )
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            location_type = ""
            _banner = sp1.select_one("a.sppb-btn-block.sppb-btn-square")
            if _banner and "temporarily closed" in _banner.text.lower():
                location_type = "Temporarily Closed"
            address = sp1.select("address")
            if not address[-1].text.strip():
                del address[-1]
            addr = [aa.replace("\xa0", " ") for aa in address[-1].stripped_strings][1:]
            if addr[-1] == "Get Directions":
                del addr[-1]
            zip_postal = " ".join(addr[-1].split(",")[1].strip().split(" ")[1:]).strip()
            country_code = "US"
            if len(zip_postal) > 5:
                country_code = "CA"
            hours = []
            _hr = sp1.find("strong", string=re.compile(r"Opening Hours"))
            if _hr:
                temp = [
                    hh.replace("\xa0", " ")
                    for hh in _hr.find_parent().find_parent().stripped_strings
                ][1:]
                if _p(temp[-1]):
                    del temp[-1]
                day = ""
                times = []
                for x, hh in enumerate(temp):
                    if hh.split(" ")[0].split(":")[0] in days:
                        if day:
                            hours.append(f"{day} {' '.join(times)}")
                        day = hh
                        times = []
                    else:
                        times.append(hh)
                    if x == len(temp) - 1:
                        hours.append(f"{day} {' '.join(times)}")
            yield SgRecord(
                page_url=page_url,
                store_number=link.number.text,
                location_name=link.storename.text,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                country_code=country_code,
                phone=sp1.select_one("div.sppb-addon-content a")
                .text.split("ext")[-1]
                .strip(),
                locator_domain=locator_domain,
                latitude=link.lat.text,
                longitude=link.lng.text,
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
