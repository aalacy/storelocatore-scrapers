from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pittsburghbluesteak.com/"
base_url = "https://pittsburghbluesteak.com/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("ul#main-menu li")[0].select("ul li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            if not page_url.startswith("http"):
                continue
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = []
            block = list(
                sp1.select("div.row.graytext div.col-md-4")[0].stripped_strings
            )
            phone = ""
            for x, bb in enumerate(block):
                if "phone:" in bb.lower():
                    phone = block[x + 1]
                    addr = block[:x]
                    break
            temp = list(
                sp1.find("h5", string=re.compile(r"Hours"))
                .find_parent()
                .stripped_strings
            )[1:]
            hours = []
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")

            href = sp1.find("a", string=re.compile(r"Get Directions"))["href"]
            try:
                coord = href.split("ll=")[1].split("&")[0].split(",")
            except:
                try:
                    coord = href.split("/dir/")[1].split("/")[0].split(",")
                except:
                    coord = href.split("/@")[1].split("/data")[0].split(",")
            try:
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.text.strip(),
                    street_address=addr[-2],
                    city=addr[-1].split(",")[0].strip(),
                    state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=coord[0],
                    longitude=coord[1],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
