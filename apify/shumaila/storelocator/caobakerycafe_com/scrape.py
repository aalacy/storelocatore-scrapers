import ssl
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager


ssl._create_default_https_context = ssl._create_unverified_context
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
website = "caobakerycafe_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.caobakerycafe.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    driver = SgChrome(
        executable_path=ChromeDriverManager().install(), user_agent=user_agent
    ).driver()
    url = "https://www.caobakerycafe.com/locations"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    contentlist = soup.findAll("div", {"class": "pm-location"})
    loclist = driver.page_source.split('<script id="popmenu-apollo-state">')[1].split(
        "</script>"
    )[0]
    loclist = loclist.split("RestaurantLocation:")[1:]
    p = 0
    for loc in loclist:
        loc = loc.split("{", 1)[1].split(',"scheduledDeliveryTimeSlots"', 1)[0]
        loc = "{" + loc + "}"
        try:
            loc = json.loads(loc)
        except:
            break
        store = loc["id"]
        phone = loc["displayPhone"]
        street, city, state = loc["fullAddress"].split(", ")
        state, pcode = state.strip().split(" ", 1)
        ccode = loc["country"]
        lat = loc["lat"]
        longt = loc["lng"]
        if "Coming Soon" in contentlist[p].text:
            continue
        title = contentlist[p].find("h4").text
        link = (
            "https://www.caobakerycafe.com"
            + contentlist[p].find("a", {"class": "details-button"})["href"]
        )
        log.info(link)
        hours = (
            contentlist[p]
            .find("div", {"class": "hours"})
            .text.replace("pm", "pm ")
            .strip()
        )
        p += 1

        hours = hours.encode("ascii", "ignore").decode("ascii")

        yield SgRecord(
            locator_domain="https://www.caobakerycafe.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
