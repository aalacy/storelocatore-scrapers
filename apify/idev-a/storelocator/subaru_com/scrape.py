from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("subaru")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.subaru.com/"
    base_url = "https://www.subaru.com/services/dealers/distances/by/bounded-location?latitude=39.857117&longitude=-98.56977&neLatitude=84.92891450547761&neLongitude=180&swLatitude=-20.626499923373608&swLongitude=-180&count=-1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for loc in locations:
            _ = loc["dealer"]
            street_address = _["address"]["street"]
            if _["address"]["street2"]:
                street_address += " " + _["address"]["street2"]
            logger.info(_["siteUrl"])
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in bs(
                    session.get(_["siteUrl"], headers=_headers).text, "lxml"
                ).select("div#hours1-app-root li")
            ]
            yield SgRecord(
                page_url=_["siteUrl"],
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["address"]["city"],
                state=_["address"]["state"],
                zip_postal=_["address"]["zipcode"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                country_code="US",
                phone=_["phoneNumber"].strip(),
                location_type=_["address"]["type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
