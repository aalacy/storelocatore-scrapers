from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("farmersnb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.farmersnb.bank/"
    base_url = "https://www.farmersnb.bank/about/convenient-locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.row.one-location")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            addr = list(link.p.stripped_strings)
            _hr = sp1.find("b", string=re.compile(r"Hours"))
            hours = []
            if _hr:
                temp = list(_hr.find_parent().stripped_strings)[1:]
                for hh in temp:
                    if hh == ":":
                        continue
                    if "Hours" in hh:
                        break
                    hours.append(hh)
            _phone = sp1.find("p", string=re.compile(r"Phone:"))
            phone = ""
            if _phone:
                phone = _phone.text.split("Fax")[0].split(":")[-1].replace("Phone", "")
            try:
                coord = res.split("google.maps.LatLng(")[1].split(");")[0].split(",")
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=link.h2.text.strip(),
                raw_address=" ".join(addr),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-").replace(",", ";"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
