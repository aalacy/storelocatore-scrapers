import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("sprouts.com")

session = SgRequests()

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}


def fetch_data(sgw: SgWriter):
    url = "https://shop.sprouts.com/api/v2/stores"
    loclist = session.get(url, headers=headers, verify=False).json()["items"]

    base_link = "https://www.sprouts.com/stores/"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_links = []
    state_links = base.find_all(class_="grid-x")[1].find_all("a")
    for state_link in state_links:
        req = session.get(state_link["href"], headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        cities = base.find(class_="grid-x").find_all(class_="cell")
        for city in cities:
            if (
                "opening" not in city.text.lower()
                and "coming soon" not in city.text.lower()
            ):
                all_links.append([city.a["href"], city, state_link["href"]])

    for i in all_links:
        link = i[0]
        log.info(link)

        store_num = i[1].find(class_="store-num").text.split("#")[-1].split(")")[0]

        try:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            if (
                store_num
                == base.find(class_="store-number").text.split("#")[-1].strip()
            ):
                got_page = True
            else:
                got_page = False
        except:
            got_page = False

        if got_page:
            script = base.find(
                "script", attrs={"type": "application/ld+json"}
            ).contents[0]
            store = json.loads(script)

            location_name = base.h1.text.strip()
            street_address = store["address"]["streetAddress"]
            city = store["address"]["addressLocality"]
            state = store["address"]["addressRegion"]
            zip_code = store["address"]["postalCode"]
            country_code = store["address"]["addressCountry"]
            store_number = store_num
            location_type = ""
            phone = store["telephone"]
            hours_of_operation = store["openingHours"]
            latitude = store["geo"]["latitude"]
            longitude = store["geo"]["longitude"]
        else:
            log.info("2nd Method..")
            store = i[1]
            store_number = ""
            hours_of_operation = ""
            location_type = ""
            latitude = ""
            longitude = ""
            link = i[2]
            for loc in loclist:
                if store_num == loc["id"]:
                    street_address = loc["address"]["address1"]
                    if str(loc["address"]["address2"]) != "None":
                        street_address = (
                            street_address + " " + str(loc["address"]["address2"])
                        )
                    city = loc["address"]["city"]
                    zip_code = loc["address"]["postal_code"]
                    state = loc["address"]["province"]
                    phone = loc["phone_number"]
                    store_number = loc["id"]
                    location_name = loc["name"]
                    latitude = loc["location"]["latitude"]
                    longitude = loc["location"]["longitude"]
                    break
            if not store_number:
                log.info("3rd Method..")
                store_number = store_num
                location_name = store.h4.text
                raw_address = list(store.find_all("p")[-1].stripped_strings)
                street_address = raw_address[0]
                city_line = raw_address[1].strip().split(",")
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                phone = raw_address[-1]
                if "-" not in phone:
                    phone = ""

        if "moved to a new location" in street_address:
            continue

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.sprouts.com/",
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
