from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bennigans")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://bennigans.com/"
    base_url = "https://bennigans.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = (
            soup.select_one("div#domestic")
            .find_next_sibling()
            .select("div.fusion-layout-column")
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            addr = []
            for aa in _.h5.find_next_siblings():
                addr += list(aa.stripped_strings)
            del addr[-1]
            try:
                coord = _.a["href"].split("!3d")[1].split("!3m")[0].split("!4d")
            except:
                try:
                    coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
                except:
                    coord = ["", ""]
            yield SgRecord(
                page_url=base_url,
                location_name=" ".join(_.h5.stripped_strings).replace("’", "'"),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
