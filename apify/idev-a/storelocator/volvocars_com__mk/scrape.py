from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
from webdriver_manager.chrome import ChromeDriverManager

logger = SgLogSetup().get_logger("")

header1 = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.volvocars.com",
    "referer": "https://www.volvocars.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
}

locator_domain = "https://www.volvocars.com/mk/"
urls = {
    "Albania": "https://www.volvocenter.al/iframe_ajax?load_scripts=dealers",
    "North Macedonia": "https://www.volvocentar.mk/iframe_ajax?load_scripts=dealers",
    "Montenegro": "https://www.volvocentar.me/iframe_ajax?load_scripts=dealers",
}


def fetch_data():
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        for country, base_url in urls.items():
            logger.info(base_url)
            driver.get(base_url)
            soup = bs(
                json.loads(bs(driver.page_source, "lxml").text)["content"], "lxml"
            )
            locations = soup.select("div.dealer_item")
            for _ in locations:
                raw_address = _.p.text.strip()
                street_address = city = state = zip_postal = ""
                addr = raw_address.split(",")
                street_address = addr[0]
                city = addr[-1].strip().split()[-1].split("-")[0]
                zip_postal = addr[-1].strip().split()[0]

                block = list(_.stripped_strings)
                phone = ""
                for x, bb in enumerate(block):
                    if bb == "T:":
                        phone = block[x + 1]
                        break
                lat, lng = (
                    _.select_one("a.location_link")["href"].split("q=")[-1].split(",")
                )
                hours = []
                days = [
                    dd.text.strip()
                    for dd in _.select("div.termin_hours")[0].select("span.week-day")
                ]
                times = [
                    dd.text.strip()
                    for dd in _.select("div.termin_hours")[0].select("span.work-hour")
                ]
                for hh in range(len(days)):
                    hours.append(f"{days[hh]} {times[hh]}")
                yield SgRecord(
                    page_url=base_url,
                    location_name=_.h2.text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country,
                    phone=phone,
                    latitude=lat,
                    longitude=lng,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
