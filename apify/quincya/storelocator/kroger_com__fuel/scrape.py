import json
import ssl
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import sglog

log = sglog.SgLogSetup().get_logger("kroger.com")

ssl._create_default_https_context = ssl._create_unverified_context

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"user-agent": user_agent}
session = SgRequests()


def get_session(retry):
    global session
    if retry:
        session = SgRequests()

    return session


def fetch_location(url, retry=0):
    try:
        session = get_session(retry)
        page_url = url.text
        log.info(page_url)
        response = session.get(page_url, headers=headers)
        location_soup = BeautifulSoup(response.text, "lxml")

        script = location_soup.find(
            "script", attrs={"type": "application/ld+json"}
        ).contents[0]
        data = json.loads(script)
        street_address = data["address"]

        location_name = location_soup.find(
            "h1", {"data-qa": "storeDetailsHeader"}
        ).text.strip()

        try:
            street_address = data["address"]["streetAddress"]
            city = data["address"]["addressLocality"]
            state = data["address"]["addressRegion"]
            zipp = data["address"]["postalCode"]
        except:
            raw_address = (
                location_soup.find(class_="StoreAddress-storeAddressGuts")
                .get_text(" ")
                .replace(",", "")
                .replace(" .", ".")
                .replace("..", ".")
                .split("  ")
            )
            if len(raw_address) != 1:
                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
                state = raw_address[2].strip()
                zipp = raw_address[3].split("Get")[0].strip()
            else:
                raw_address = list(
                    location_soup.find(
                        class_="StoreAddress-storeAddressGuts"
                    ).stripped_strings
                )[0].split(",")
                street_address = " ".join(raw_address[0].split()[:-1])
                city = raw_address[0].split()[-1]
                state = raw_address[1].split()[0]
                zipp = raw_address[1].split()[1]
        country_code = "US"
        store_number = page_url.split("/")[-1]
        try:
            phone = data["telephone"]
        except:
            try:
                phone = location_soup.find(class_="PhoneNumber-phone").text.strip()
            except:
                phone = ""
        lat = data["geo"]["latitude"]
        lng = data["geo"]["longitude"]
        hours = " ".join(data["openingHours"])

        try:
            loc_type = ", ".join(
                list(
                    location_soup.find(
                        class_="StoreServices-departmentsList"
                    ).stripped_strings
                )
            )
            if "gas" not in loc_type.lower() and "diesel" not in loc_type.lower():
                continue
        except:
            continue

        return SgRecord(
            locator_domain="https://www.kroger.com/",
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
        )
    except Exception as e:
        if retry < 3:
            return fetch_location(url, retry + 1)

        log.error(e)

        return None


def fetch_data():

    base_link = "https://www.kroger.com/storelocator-sitemap.xml"

    response = session.get(base_link, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    urls = soup.find_all("loc")[:-1]

    for url in urls:
        yield fetch_location(url)


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    data = fetch_data()
    for row in data:
        writer.write_row(row)
