from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("patioenclosures")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.patioenclosures.com"
    base_url = "https://www.patioenclosures.com/sitemap.aspx"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        data = (
            soup.select_one("ul#ctl00_mainContent_menu_UL")
            .find("a", string=re.compile(r"Find Your Location"))
            .find_next_sibling()
            .select("li")
        )
        for i in data:
            links = i.find("a")["href"]
            if "directions" in links or "photos" in links or "ideas" in links:
                continue
            page_url = locator_domain + links
            logger.info(page_url)
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")

            if "canada" in page_url:
                country_code = "CA"
            else:
                country_code = "US"
            details = soup1.find("div", {"class": "branch-intro-copy"})
            if details:
                info = list(
                    soup1.find("div", {"class": "branch-address"}).stripped_strings
                )
                location_name = soup1.find("h2").text
                if "Location coming soon!" in info:
                    continue

                _info = " ".join(info)
                if "By Appointment Only" == _info or "By Appointment Only!" == _info:
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    state = "<MISSING>"
                    zipp = "<MISSING>"
                else:
                    addr = parse_address_intl(" ".join(info))
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    street_address = street_address
                    city = addr.city
                    state = addr.state
                    zipp = addr.postcode
                phone = (
                    details.find_all("li")[1]
                    .text.replace("Local:", "")
                    .replace("Phone:", "")
                    .strip()
                )
                hour = " ".join(
                    list(
                        soup1.find("ul", {"class": "two-column-list"}).stripped_strings
                    )
                )
                if "Monday" in hour:
                    hours_of_operation = hour
                else:
                    hours_of_operation = "<MISSING>"

            else:
                location_name = soup1.find("h1").text.capitalize()
                row_adr = soup1.find("div", {"class": "branch-details"})
                street_address = "".join(
                    list(row_adr.find_all("p")[0].stripped_strings)[:-1]
                )
                city = list(row_adr.find_all("p")[0].stripped_strings)[-1].split(",")[0]
                state = (
                    list(row_adr.find_all("p")[0].stripped_strings)[-1]
                    .split(",")[1]
                    .split(" ")[1]
                )
                zipp = " ".join(
                    list(row_adr.find_all("p")[0].stripped_strings)[-1]
                    .split(",")[1]
                    .split(" ")[2:]
                )

                if "colorado" in page_url or "tampa" in page_url:
                    phone = list(row_adr.find_all("p")[2].stripped_strings)[1].replace(
                        "Local:", "813-620-0931"
                    )
                    hours_of_operation = " ".join(
                        list(row_adr.find_all("p")[1].stripped_strings)
                    )
                else:
                    phone = list(row_adr.find_all("p")[3].stripped_strings)[1]
                    hours_of_operation = " ".join(
                        list(row_adr.find_all("p")[2].stripped_strings)
                    )

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                phone=phone.split(":")[0].replace("Toll-free", ""),
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation.replace("By Appointment", ""),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
