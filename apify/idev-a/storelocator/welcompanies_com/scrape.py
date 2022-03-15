from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("welcompanies")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.welcompanies.com"
base_url = "https://www.welcompanies.com/partner-with-wel/warehousing/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#warehouse-locations div.map__row")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.p.stripped_strings)
            try:
                coord = (
                    link.select_one("div.map__map a")["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=link.h2.text.strip(),
                street_address=addr[0],
                city=" ".join(addr[1].split(" ")[:-2]).replace(",", ""),
                state=addr[1].split(" ")[-2].strip(),
                zip_postal=addr[1].split(" ")[-1].strip(),
                country_code="US",
                phone=addr[-1],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(addr[2:-1]),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
