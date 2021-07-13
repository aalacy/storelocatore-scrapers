from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("sunterramarket")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sunterramarket.com"
base_url = "https://www.sunterramarket.com/Locations"


def fetch_data():
    with SgChrome() as driver:
        driver.get(locator_domain)
        driver.find_element_by_css_selector('button[name="SignInButton"]').click()
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.address-list-inner li")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.a:
                continue
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            driver.get(page_url)
            coord = json.loads(
                driver.page_source.split("var locationOfSunterra =")[1]
                .split(";")[0]
                .strip()
            )
            sp1 = bs(driver.page_source, "lxml")
            temp = list(sp1.select_one("div.address-block").stripped_strings)
            hours = []
            for x, hh in enumerate(temp):
                if "Hours" in hh:
                    for hr in temp[x + 1 :]:
                        if "Reopened" in hr or "pickup" in hr or "apologize" in hr:
                            continue
                        if "email" in hr.lower() or "hour" in hr.lower():
                            break
                        hours.append(hr)
                    break
            addr = list(link.p.stripped_strings)
            phone = ""
            if "Phone" in addr[-1]:
                phone = (
                    addr[-1]
                    .split(":")[-1]
                    .replace("Phone", "")
                    .split("Office")[-1]
                    .strip()
                )
                del addr[-1]
            location_name = link.h4.text.split("-")[-1].strip()
            location_type = ""
            if "temporarily closed" in location_name.lower():
                location_type = "temporarily closed"
                location_name = location_name.split("(")[0]
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=" ".join(addr[1].split(",")[1].strip().split(" ")[1:]),
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord["lat"],
                longitude=coord["lng"],
                location_type=location_type,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
