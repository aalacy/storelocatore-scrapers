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
        locator_domain = "http://sukiyaki-restaurants.com/"
        base_url = "http://sukiyaki-restaurants.com/en/locations.html#"
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul.alllocs li.qc ul"
        )
        for _ in locations:
            block = list(_.stripped_strings)
            location_name = block[0]
            hours_of_operation = ""
            if "(Temporarily Closed)" in location_name:
                location_name = location_name.replace("(Temporarily Closed)", "")
                hours_of_operation = "Temporarily Closed"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=block[1],
                city=block[2],
                state=block[3],
                zip_postal=block[4],
                country_code="CA",
                phone=block[-1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
