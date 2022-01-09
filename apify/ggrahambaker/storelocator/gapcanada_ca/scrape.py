import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("gapcanada_ca")


def addy_ext(addy):
    addy = addy.split(",")
    city = addy[0]
    state_zip = addy[1].strip().split(" ")
    if len(state_zip) == 4:
        logger.info("four!!")
    else:
        state = state_zip[0]
        zip_code = state_zip[1] + " " + state_zip[2]
    return city, state, zip_code


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://www.gapcanada.ca/"
    ext = "stores#browse-by-state-section"
    r = session.get(locator_domain + ext, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")
    ul = soup.find("ul", {"id": "browse-content"})

    locs = [locator_domain[:-1] + l["href"] for l in ul.find_all("a")]
    city_links = []
    for l in locs:
        r = session.get(l, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        links = [a["href"] for a in soup.find_all("a", {"class": "ga-link"})]
        for link in links:
            if "?bc=true" in link:
                continue
            city_links.append(locator_domain[:-1] + link)

    link_list = []
    for city in city_links:
        r = session.get(city, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        links = [a["href"] for a in soup.find_all("a", {"class": "view-store"})]
        for link in links:
            if "?bc=true" in link:
                continue
            link_list.append(locator_domain[:-1] + link)

    if "https://www.gapcanada.ca/stores/on/london/" not in link_list:
        link_list.append("https://www.gapcanada.ca/stores/on/london/")

    for link in link_list:
        logger.info(link)
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        addy = soup.find("p", {"class": "address"}).find_all("span")
        street_address = " ".join(addy[0].text.split())

        city, state, zip_code = addy_ext(" ".join(addy[1].text.split()))

        google_link = soup.find("a", {"class": "directions"})["href"]

        start = google_link.find("daddr=")
        coords = google_link[start + 6 :].split(",")

        phone_number = soup.find("a", {"class": "phone"}).text.strip()
        if phone_number == "":
            phone_number = "<MISSING>"

        hours_div = soup.find("div", {"class": "hours"})
        dayparts = hours_div.find_all("span", {"class": "daypart"})
        times = hours_div.find_all("span", {"class": "time"})
        hours = ""
        for i, day in enumerate(dayparts):
            hours += dayparts[i].text.strip() + " " + times[i].text.strip() + " "
        hours = hours.replace("\n", "").strip()
        hours = (re.sub(" +", " ", hours)).strip()

        country_code = "CA"
        store_number = link.split("-")[-1]
        if locator_domain in store_number:
            store_number = ""

        location_type = soup.find(class_="store-carries").text.strip()
        if "," in location_type:
            location_name = "Gap"
        else:
            location_name = location_type

        lat = coords[0]
        longit = coords[1]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
