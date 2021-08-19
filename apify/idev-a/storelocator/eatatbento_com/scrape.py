from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("eatatbento")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


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


def _h(val):
    if val:
        return val
    else:
        return "closed"


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.eatatbento.com/"
        base_url = "https://www.eatatbento.com/locations/"
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul.products li.product div.overflow")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.a:
                continue
            soup1 = bs(session.get(link.a["href"], headers=_headers).text, "lxml")
            logger.info(link.a["href"])
            _hr = soup1.find("a", string=re.compile(r"HOURS", re.IGNORECASE))
            hours = []
            if _hr:
                temp = list(_hr.find_parent().find_parent().stripped_strings)[1:]
                if "Soft" in temp[0]:
                    del temp[0]
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]} {temp[x+1]}")

            phone = ""
            if soup1.find("a", href=re.compile(r"tel:")):
                phone = soup1.find("a", href=re.compile(r"tel:")).text
            addr = list(link.select_one("span.price").stripped_strings)
            try:
                coord = (
                    soup1.select_one("div.inner iframe")["src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")
                )
                latitude = coord[1].split("!3m")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=link.a["href"],
                location_name=soup1.h1.text,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=latitude[0],
                longitude=coord[0],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
