import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://bigcatchseafoodhouse.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="rank-math-review-data")
    locator_domain = "bigcatchseafoodhouse.com"

    for item in items:

        street_address = item.find(class_="contact-address-address").text.strip()
        city = item.find(class_="contact-address-locality").text.strip()
        state = item.find(class_="contact-address-region").text.strip()
        zip_code = item.find(class_="contact-address-postalcode").text.strip()

        location_name = "Big Catch Seafood House " + city
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find_all("a")[1].text.strip()

        try:
            hours_of_operation = " ".join(
                list(
                    item.find(
                        class_="olderdata rank-math-contact-hours-details rank-math-gear-snippet-content"
                    ).stripped_strings
                )
            )
        except:
            hours_of_operation = " ".join(
                list(item.find_all("div")[-1].stripped_strings)[1:]
            )

        map_link = item.a["href"]
        # Maps
        req = session.get(map_link, headers=headers)
        maps = BeautifulSoup(req.text, "lxml")

        try:
            raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
            latitude = raw_gps.split("=")[1].split("%2C")[0]
            longitude = raw_gps.split("%2C")[1].split("&")[0]
        except:
            try:
                map_str = maps.find("meta", attrs={"itemprop": "image"})["content"]
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        if "765 N. Milliken" in street_address:
            latitude = "34.070946"
            longitude = "-117.5614592"

        link = (
            "https://bigcatchseafoodhouse.com/locations/"
            + city.replace(" ", "-").lower()
        )

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
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
