from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("trustmark")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://trustmark.com"
    base_url = "https://trustmark.com/about-us/locations.locsearch.html?lat=32.3028311&lng=-90.1838507&dist=5000&facet=*ATM%2FITM"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = locator_domain + _["pagePath"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                "".join(hh.stripped_strings)
                for hh in sp1.select("table.display-hours")[0].select("tr")
            ]
            location_type = []
            for service in [ss.text for ss in sp1.select("h4.service-title")]:
                if "bank services" in service.lower():
                    location_type.append("branch")
                if "atm services" in service.lower():
                    location_type.append("atm")
            yield SgRecord(
                page_url=page_url,
                store_number=_["storeCode"],
                location_name=_["branchTitle"].split("offering")[0],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["branchPhone"],
                locator_domain=locator_domain,
                location_type=",".join(location_type),
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
