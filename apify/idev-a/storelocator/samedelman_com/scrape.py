from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import re


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


def _phone(val):
    return (
        val.replace(")", "")
        .replace("(", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://www.samedelman.com/"
    base_url = "https://www.samedelman.com/store-locations"
    with SgChrome() as driver:
        driver.get(base_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='content']"))
        )
        soup = bs(driver.page_source, "lxml")
        locations = soup.select(
            "div#content div.row.no-gutters div.row.no-gutters div.row.no-gutters div.component-content"
        )
        for _ in locations:
            if not re.search(r"store hours", _.text, re.IGNORECASE):
                continue
            block = list(_.stripped_strings)
            del block[-1]
            addr = list(_.h4.stripped_strings)
            if "Shanghai" in addr:
                continue
            phone = addr[-1]
            if not _phone(phone):
                del addr[-1]
                phone = addr[-1]
            state_zip = addr[-2].split(",")[1].strip().split(" ")
            hours = []
            for x, bb in enumerate(block):
                if re.search(r"Store Hours", bb, re.IGNORECASE):
                    hours = block[x + 1 :]
                    break
            coord = ["", ""]
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                pass
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=addr[-3],
                city=addr[-2].split(",")[0].strip(),
                state=state_zip[0],
                zip_postal=state_zip[-1],
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
