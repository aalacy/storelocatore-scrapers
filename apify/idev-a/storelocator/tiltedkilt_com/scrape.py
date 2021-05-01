from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tiltedkilt")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://tiltedkilt.com/"
    base_url = "https://tiltedkilt.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.state-container .location-row")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(_.select_one(".address").stripped_strings)
            street_address = " ".join(addr[:-1])
            hours = [
                "".join(hh.stripped_strings)
                for hh in sp1.select("div.hours-tooltip div.line")
            ]
            if len(hours) == 1 and hours[0].startswith(":"):
                hours = ["closed"]
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("div.name").text.strip(),
                street_address=street_address,
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=_.select_one("div.phone").text.strip(),
                locator_domain=locator_domain,
                latitude=sp1.select_one("div#gMap")["data-lat"],
                longitude=sp1.select_one("div#gMap")["data-lng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
