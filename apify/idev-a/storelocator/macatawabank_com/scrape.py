from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("macatawabank")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.split(":")[-1]
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
    )


def fetch_data():
    locator_domain = "https://macatawabank.com"
    base_url = "https://macatawabank.com/info/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.find_all("a", href=re.compile(r"/info/locations/"))
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = sp1.find("h2", string=re.compile(r"^Address", re.IGNORECASE))
            if _addr:
                if _addr.find_next_sibling("a"):
                    addr = list(_addr.find_next_sibling("a").stripped_strings)
                else:
                    addr = list(_addr.find_next_sibling("p").stripped_strings)
            else:
                addr = list(
                    sp1.find(
                        "a",
                        title=re.compile(r"^by clicking this link you", re.IGNORECASE),
                    ).stripped_strings
                )
            _contact = sp1.find("h2", string=re.compile(r"^Contact"))

            _hr = sp1.find(
                "h2", string=re.compile(r"^Lobby & Drive-up Hours", re.IGNORECASE)
            )
            hours = []
            temp = []
            if not _hr:
                _hr = sp1.find("h2", string=re.compile(r"^Office Hours", re.IGNORECASE))
            if _hr:
                temp = list(_hr.find_parent().stripped_strings)[1:]
                for hh in temp:
                    if "drive" in hh.lower() or "lobby" in hh.lower():
                        break
                    hours.append(hh)

            phone = ""
            if _contact:
                cont = list(_contact.find_parent().stripped_strings)
                for cc in cont:
                    if _p(cc).isdigit():
                        phone = cc.split(":")[-1].strip()
                        break
                if not temp:
                    for x, cc in enumerate(cont):
                        if "Monday" in cc:
                            temp = cont[x:]
                            break
                    for x, cc in enumerate(temp):
                        if (
                            "phone" in cc.lower()
                            or "administration" in cc.lower()
                            or "human" in cc.lower()
                        ):
                            break
                        hours.append(cc)

            coord = sp1.iframe["src"].split("!1d")[1].split("!3f")[0].split("!2d")
            location_type = "branch"
            location_name = sp1.h1.text.strip()
            if "atm" in location_name.lower():
                location_type = "atm"
            elif "branch" in location_name.lower():
                location_type = "branch"
            if sp1.find("h2", string=re.compile(r"^ATM")):
                location_type += ", atm"
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
