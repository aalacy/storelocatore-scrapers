from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("domesticuniform")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.domesticuniform.com/"
    base_url = "https://www.domesticuniform.com/new-customers/facilities/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#two_column p")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.stripped_strings)
            zip_postal = addr[-1].split(",")[-1].strip().split(" ")[-1].strip()
            if not zip_postal.replace("-", "").strip().isdigit():
                zip_postal = ""
            yield SgRecord(
                page_url=base_url,
                location_name=addr[0],
                street_address=" ".join(addr[1:-1]),
                city="".join(addr[-1].split(",")[:-1]).replace(",", ""),
                state=addr[-1].split(",")[-1].strip().split(" ")[0].strip(),
                zip_postal=zip_postal,
                country_code="US",
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
