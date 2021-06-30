from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ptandrehab")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://ptandrehab.com/"
    base_url = "https://ptandrehab.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location-information div.single-location")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.h4.a["href"]
            addr = list(link.p.a.stripped_strings)
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            temp = list(sp1.select_one("div.business-hours").stripped_strings)[1:]
            hours = []
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")

            coord = link.p.a["href"].split("/@")[1].split("/data")[0].split(",")
            yield SgRecord(
                page_url=page_url,
                location_name=link.h4.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=link.select_one("a.text-black.font-bold ").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
