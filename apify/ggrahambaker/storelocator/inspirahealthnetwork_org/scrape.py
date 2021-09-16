import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.inspirahealthnetwork.org"
    ext = "/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.find(
        "script", attrs={"data-drupal-selector": "drupal-settings-json"}
    ).contents[0]
    locs = json.loads(js)["locationsMap"]["data"]

    link_list = []
    for loc in locs:
        stores = BeautifulSoup(loc["content"], "lxml").find_all(
            class_="mapboxgl-popup--location-slider--wrap"
        )
        for store in stores:
            link_tag = locator_domain + store.find(role="article").a["href"]
            link_list.append(link_tag)

    for link in link_list:
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.content, "lxml")

        country_code = "US"

        info = soup.find("script", {"type": "application/ld+json"}).contents[0]
        loc = json.loads(info)

        addy = loc["address"]

        street_address = addy["streetAddress"].replace("\n", " ").strip()
        city = addy["addressLocality"].strip()
        state = addy["addressRegion"].strip()
        zip_code = addy["postalCode"].strip()

        try:
            phone_number = (
                soup.find(class_="phone").a.text.replace("Get Directions", "").strip()
            )
        except:
            phone_number = "<MISSING>"

        coords = loc["geo"]
        lat = coords["latitude"]
        longit = coords["longitude"]

        try:
            hours = loc["openingHours"].strip()
        except:
            hours = "<MISSING>"

        location_name = loc["name"].strip()
        store_number = "<MISSING>"
        try:
            location_type = ", ".join(
                list(soup.find(class_="related-services-items").stripped_strings)
            )
        except:
            location_type = "<MISSING>"

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
