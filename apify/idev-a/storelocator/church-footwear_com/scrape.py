from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("church-footwear")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.church-footwear.com/"
    base_url = "https://www.church-footwear.com/us/en/store-locator.html"
    with SgFirefox() as driver:
        driver.get(base_url)
        for link in driver.find_elements_by_css_selector(
            "div#store-box-list div.store-box"
        ):
            driver.execute_script("arguments[0].click();", link)
            sp1 = bs(driver.page_source, "lxml")
            hours = []
            for hh in sp1.select("div.store-detail-container div.day-of-week"):
                hr = list(hh.stripped_strings)
                if hr[1].split(":")[1].strip() == "--":
                    continue
                hours.append("".join(hr))
            addr = parse_address_intl(
                f"{link.find_element_by_css_selector('p.store-address').get_attribute('innerHTML').strip()} {link.find_element_by_css_selector('.store-city-zip').get_attribute('innerHTML').strip()}"
            )
            yield SgRecord(
                page_url=base_url,
                store_number=link.get_attribute("data-store-id"),
                location_name=link.get_attribute("data-name"),
                street_address=link.find_element_by_css_selector(".store-address")
                .get_attribute("innerHTML")
                .strip(),
                city=link.get_attribute("data-city"),
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=link.get_attribute("data-country"),
                phone=link.find_element_by_css_selector(".store-phone")
                .get_attribute("innerHTML")
                .strip(),
                locator_domain=locator_domain,
                latitude=link.get_attribute("data-lat"),
                longitude=link.get_attribute("data-lng"),
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
