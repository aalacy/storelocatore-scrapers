from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re

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
        links = soup.select("ul.products li.product div.overflow a")
        for link in links:
            soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            block = soup1.find("div", string=re.compile(r"ORDER ONLINE", re.IGNORECASE))
            if not block:
                block = soup1.find(
                    "p", string=re.compile(r"ORDER ONLINE", re.IGNORECASE)
                )
            _detail = block.next_sibling
            detail = None
            hh = None
            if not _detail.p:
                detail = list(_detail.stripped_strings)
                hh = list(_detail.next_sibling.stripped_strings)
            else:
                detail = list(_detail.select("p")[0].stripped_strings)
                hh = list(_detail.select("p")[1].stripped_strings)

            del hh[0]
            if "*Soft" in hh[0]:
                del hh[0]
            if len(hh) % 2 != 0:
                del hh[0]
            hours = []
            for x in range(0, len(hh), 2):
                hours.append(f"{hh[x]}: {hh[x+1]}")

            phone = detail[-1]
            if not _phone(phone):
                phone = ""
            ss = detail[1].strip().split(",")
            yield SgRecord(
                page_url=link["href"],
                location_name=soup1.h1.text,
                street_address=detail[0],
                city=ss[0],
                state=ss[1].strip().split(" ")[0],
                zip_postal=ss[1].strip().split(" ")[-1],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
