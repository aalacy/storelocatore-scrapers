from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("purebarre_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    url = "https://members.purebarre.com/api/brands/purebarre/locations?open_status=external&geoip="
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(url)
        time.sleep(20)
        array = json.loads(driver.find_element(By.CSS_SELECTOR, "body").text)
        for item in array["locations"]:
            name = item["name"]
            coming = item["coming_soon"]
            lat = item["lat"]
            lng = item["lng"]
            if "address2" in item:
                add = item["address"] + " " + str(item["address2"])
            add = add.strip()
            city = item["city"]
            state = item["state"]
            zc = item["zip"]
            lurl = item["site_url"]
            phone = item["phone"]
            country = item["country_code"]
            website = "purebarre.com"
            typ = "Location"
            hours = ""
            store = item["clubready_id"]
            DFound = False
            if lurl is not None:
                logger.info(("Pulling Hours For %s..." % lurl))
                r2 = session.get(lurl, headers=headers)
                logger.info(f"Response: {r2}")
                if r2.status_code == 404:
                    continue
                lines = r2.iter_lines()
                for line2 in lines:
                    if "day&quot;:" in line2:
                        DFound = True
                        day = line2.split("&quot;")[1]
                        hrs = ""
                    if "&quot;," in line2 and DFound:
                        hrs = line2.split("&quot;")[1]
                        g = next(lines)
                        hrs = hrs + "-" + g.split("&quot;")[1]
                        if hours == "":
                            hours = day + ": " + hrs
                        else:
                            hours = hours + "; " + day + ": " + hrs
            else:
                lurl = "<MISSING>"
                hours = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if coming is False:
                yield SgRecord(
                    locator_domain=website,
                    page_url=lurl,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
