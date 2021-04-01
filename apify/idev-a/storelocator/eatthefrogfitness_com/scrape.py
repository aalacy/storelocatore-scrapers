from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import demjson
from sgscrape.sgpostal import parse_address_intl
import us

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def get_country_by_code(code=""):
    if not code:
        return "US"

    if us.states.lookup(code):
        return "US"
    elif code in ca_provinces_codes:
        return "CA"
    else:
        return "US"


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.eatthefrogfitness.com/"
        base_url = "https://www.eatthefrogfitness.com/"
        res = session.get(base_url, headers=_headers).text
        locations = demjson.decode(
            res.split("var locations =")[1].split("var y = 0;")[0].strip()[:-1]
        )
        for _ in locations:
            hours_of_operation = ""
            if _["comingSoon"] == "True":
                hours_of_operation = "Coming Soon"
            addr = parse_address_intl(
                " ".join(list(bs(_["address"], "lxml").stripped_strings))
            )
            yield SgRecord(
                page_url="https://www.eatthefrogfitness.com/#locations",
                store_number=_["keyid"],
                location_name=_["locationName"],
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=get_country_by_code(addr.state),
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
