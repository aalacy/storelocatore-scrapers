from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mycarecompass")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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


def fetch_data():
    with SgChrome(executable_path=r"./chromedriver.exe") as driver:
        locator_domain = "https://www.flemingssteakhouse.com/"
        base_url = "https://www.flemingssteakhouse.com/locations/"
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("ul.locations li a")
        logger.info(f"{len(links)} locations found")
        for link in links:
            logger.info(link["href"])
            driver.get(link["href"])
            soup1 = bs(driver.page_source, "lxml")
            block = soup1.find("p", string=re.compile(r"^Address", re.IGNORECASE))
            _content = list(block.find_next_sibling("a").stripped_strings)
            hour_block = soup1.find("p", string=re.compile(r"^Hours"))
            hours = []
            for hh in list(hour_block.find_next_sibling("p").stripped_strings):
                if hh == "Curbside Pickup":
                    break
                hours.append(hh)

            yield SgRecord(
                store_number=soup1.select_one("a.make-favorite")["data-id"],
                page_url=link["href"],
                location_name=soup1.h1.text.strip(),
                street_address=_content[0],
                city=_content[1].split(",")[0].strip(),
                state=_content[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=_content[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=_content[-1],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours[2:])),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
