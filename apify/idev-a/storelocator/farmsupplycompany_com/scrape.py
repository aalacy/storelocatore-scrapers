from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    locator_domain = "https://www.farmsupplycompany.com/"
    base_url = "https://www.farmsupplycompany.com/locations/"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div#locations div.location")
        for _ in locations:
            info = list(_.select("p")[0].stripped_strings)
            hours = []
            for hh in list(_.select("p")[2].stripped_strings)[1:]:
                if "Pump" in hh:
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text,
                street_address=info[0],
                city=_.h2.text,
                state="CA",
                country_code="US",
                phone=info[1],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
