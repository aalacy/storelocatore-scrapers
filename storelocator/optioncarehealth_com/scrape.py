from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("optioncarehealth")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://optioncarehealth.com"
    base_url = "https://optioncarehealth.com/option-care-health-locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.find-location__search-results div.location-card")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            ll = link.select("ul.location-card-meta li")
            addr = list(ll[0].stripped_strings)
            coord = ll[-1].a["href"].split("query=")[1].split("&")[0].split(",")
            yield SgRecord(
                page_url=page_url,
                location_name=link.h5.text.strip(),
                street_address=" ".join(addr[:-1]).replace("Benton Business Park", ""),
                city=addr[-1].split(",")[0].strip(),
                state=" ".join(addr[-1].split(",")[1].strip().split(" ")[:-1]),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=ll[1].text.strip().split(":")[-1].replace("Phone", ""),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
