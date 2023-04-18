from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("bigjohnsteakandonion")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://bigjohnsteakandonion.net/"
    base_url = "https://bigjohnsteakandonion.net/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("select.quicklinks_list option")
        logger.info(f"{len(links)} found")
        for link in links:
            if link["value"] == "none":
                continue
            page_url = locator_domain + link["value"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            addr = parse_address_intl(sp1.select_one("div.location_city p").text)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            for tr in sp1.select("table.hours tr")[1:]:
                tds = tr.select("td")
                hours.append(f"{tds[0].text}: {tds[1].text}-{tds[2].text}")
            coord = res.split("center:")[1].split("zoom:")[0].strip()[1:-2].split(",")
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("div.location_city h1").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=sp1.select("div.location_city p")[1].text.split("||")[0].strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
