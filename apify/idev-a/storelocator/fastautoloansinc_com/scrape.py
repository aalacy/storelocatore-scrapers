from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


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


days = ["", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://fastautoloansinc.com/"
        base_url = "https://fastautoloansinc.com/closest-stores?loan_type=all&num=0"
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["locations"]:
            page_url = locator_domain + _["store_url"]
            soup = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            if soup.select("#demo p"):
                hours = list(soup.select("#demo p")[-2].stripped_strings)[1:]
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_code"],
                location_name=_["business_name"],
                street_address=f"{_['address_line_1']} {_.get('address_line_2', '')}",
                city=_["locality"],
                state=_["administrative_area"],
                zip_postal=_["postal_code"],
                country_code=_["country"],
                phone=_["primary_phone"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                location_type=_["business_unit_type"],
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
