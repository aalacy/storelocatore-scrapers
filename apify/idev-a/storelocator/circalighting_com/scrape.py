from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from webdriver_manager.chrome import ChromeDriverManager
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("circalighting")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.circalighting.com"
base_url = "https://www.circalighting.com/showrooms/"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    soup = bs(driver.page_source, "lxml")
    locations = soup.select("div.category-cms .pagebuilder-column")
    for _ in locations:
        if not _.select_one("div.more"):
            continue
        if "Coming Soon" in _.select_one("div.more").text:
            continue
        block = list(_.select_one("div.more").stripped_strings)
        if "Now Open" in block[1]:
            del block[1]
        page_url = _.select("div.more a")[-1]["href"]
        if not page_url.startswith("http"):
            page_url = locator_domain + page_url
        block = [
            bb
            for bb in block
            if bb != "MAKE APPOINTMENT"
            and "Opening" not in bb
            and "More Information" not in bb
        ]
        phone = ""
        if "Phone" in block[3]:
            phone = block[3].replace("Phone", "").strip()
        hours = []
        if len(block) >= 5:
            hours = block[4:]
        city_state = block[2].split(",")
        city = state = zip_postal = ""
        country = "US"
        if len(city_state) == 1:
            country = "UK"
            city = block[2].split(" ")[0].strip()
            zip_postal = " ".join(block[2].split(" ")[1:])
        else:
            city = city_state[0]
            state = city_state[1].strip().split(" ")[0].strip()
            zip_postal = city_state[1].strip().split(" ")[1].strip()
        logger.info(page_url)
        driver.get(page_url)
        sp1 = bs(driver.page_source, "lxml")
        try:
            coord = json.loads(
                sp1.text.split("const myLatLng =")[1].split(";")[0].strip()
            )
        except:
            try:
                _coord = (
                    sp1.select_one("ul.hours")
                    .find_next_sibling("a")
                    .find_next_sibling("a")["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
                coord = {"lat": _coord[0], "lng": _coord[1]}
            except:
                coord = {"lat": "", "lng": ""}
                import pdb

                pdb.set_trace()

        yield SgRecord(
            page_url=page_url,
            location_name=block[0],
            street_address=block[1],
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country,
            phone=phone,
            latitude=coord["lat"],
            longitude=coord["lng"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
