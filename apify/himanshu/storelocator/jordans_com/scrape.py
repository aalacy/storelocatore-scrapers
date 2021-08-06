import json

from bs4 import BeautifulSoup
from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://www.jordans.com"
    r = session.get(base_url + "/content/about-us/store-locations")
    soup = BeautifulSoup(r.text, "lxml")

    main = soup.find("div", {"class": "left-sidebar-section-30"}).find_all("a")
    for atag in main:
        if atag.has_attr("href"):
            link = atag["href"]
            r1 = session.get(link)
            soup1 = BeautifulSoup(r1.text, "lxml")
            if soup1.find("script", type="application/ld+json") is not None:
                loc = json.loads(
                    soup1.find("script", type="application/ld+json").contents[0]
                )
                store = []
                store.append("https://www.jordans.com")
                store.append(link)
                store.append(loc[0]["name"])
                store.append(loc[0]["address"]["streetAddress"])
                store.append(loc[0]["address"]["addressLocality"])
                store.append(loc[0]["address"]["addressRegion"])
                store.append(loc[0]["address"]["postalCode"])
                store.append("US")
                store.append("<MISSING>")
                store.append(loc[0]["telephone"])
                if "Not A Retail Location" in soup1.text:
                    location_type = "Corporate Offices and Distribution Center"
                else:
                    location_type = "Retail Location"
                store.append(location_type)
                latitude = loc[0]["geo"]["latitude"]
                longitude = loc[0]["geo"]["longitude"]
                if "50 Walkers" in loc[0]["address"]["streetAddress"]:
                    latitude = "42.520224"
                    longitude = "-71.090348"
                store.append(latitude)
                store.append(longitude)
                store.append(" ".join(loc[0]["openingHours"]))

                sgw.write_row(
                    SgRecord(
                        locator_domain=store[0],
                        page_url=store[1],
                        location_name=store[2],
                        street_address=store[3],
                        city=store[4],
                        state=store[5],
                        zip_postal=store[6],
                        country_code=store[7],
                        store_number=store[8],
                        phone=store[9],
                        location_type=store[10],
                        latitude=store[11],
                        longitude=store[12],
                        hours_of_operation=store[13],
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
