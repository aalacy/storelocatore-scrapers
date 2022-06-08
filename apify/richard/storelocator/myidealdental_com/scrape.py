import json
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("myidealdental_com")

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}

session = SgRequests()


def fetch_data(sgw: SgWriter):

    url = "https://www.myidealdental.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    divlist = soup.find("div", {"class": "locations-list-wrapper"}).findAll(
        "li", {"class": "locations-list-item"}
    )
    for div in divlist:
        link = div.find("div", {"class": "location-links"}).find("a")["href"]
        logger.info(link)

        location_id = div["data-office-id"]
        location_type = "Location"

        r = session.get(link, headers=headers)
        try:
            base = BeautifulSoup(r.text, "lxml")
            js = base.find("script", attrs={"type": "application/ld+json"}).contents[0]
            data = json.loads(js)
            location_title = data["name"]
            got_page = True
        except:
            got_page = False

        if got_page:
            street_address = data["address"]["streetAddress"]
            city = data["address"]["addressLocality"]
            zipcode = data["address"]["postalCode"]
            state = data["address"]["addressRegion"]
            phone = data["telephone"]
            phone = (
                data["telephone"][0:3]
                + "-"
                + data["telephone"][3:6]
                + "-"
                + data["telephone"][6 : len(data["telephone"])]
            )
            phone = phone.replace("--", "-")
            lat = data["geo"]["latitude"]
            lon = data["geo"]["longitude"]

            hours_of_operation = ""
            raw_hours = data["openingHoursSpecification"]
            for hours in raw_hours:
                day = hours["dayOfWeek"]
                if len(day[0]) != 1:
                    day = " ".join(hours["dayOfWeek"])
                try:
                    opens = hours["opens"]
                    closes = hours["closes"]
                    if opens != "" and closes != "":
                        clean_hours = day + " " + opens + "-" + closes
                except:
                    clean_hours = day + " Closed"
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
        else:
            location_title = div.h3.text
            raw_address = list(div.address.stripped_strings)
            street_address = raw_address[1]
            city_line = (
                raw_address[2].replace("\n\t", " ").replace("\t", "").strip().split(",")
            )
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zipcode = city_line[-1].strip().split()[1].strip()
            phone = div.find(class_="office-phone-swap").text
            lat = div["data-lat"]
            lon = div["data-lng"]
            hours_of_operation = ""

        if "affiliated location" in div.text.lower():
            location_type = "Affiliated Location"

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.myidealdental.com/",
                page_url=link,
                location_name=location_title,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code="US",
                store_number=location_id,
                phone=phone,
                location_type=location_type,
                latitude=lat,
                longitude=lon,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
