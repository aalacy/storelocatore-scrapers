from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("capitalbanktx")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.capitalbanktx.com"
base_url = "https://www.capitalbanktx.com/Locations.aspx"


def _p(val):
    return (
        val.split(":")[-1]
        .replace("Phone", "")
        .replace("(", "")
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
        links = soup.select("table.Subsection-Table table")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.p.stripped_strings)[1:]
            if "Fax" in addr[-1]:
                del addr[-1]
            phone = ""
            if _p(addr[-1]):
                phone = addr[-1].split(":")[-1].replace("Phone", "")
            hours = []
            for hh in link.select("td")[-1].stripped_strings:
                if "Lobby" in hh:
                    continue
                if "Drive-Thru" in hh:
                    break
                hours.append(hh.strip())
            try:
                yield SgRecord(
                    page_url=base_url,
                    location_name=link.caption.text.strip(),
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
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
