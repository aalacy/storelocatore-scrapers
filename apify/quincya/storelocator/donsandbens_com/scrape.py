import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://donsandbens.com"

    base_link = "https://donsandbens.com/pages/locations"

    with SgRequests() as http:
        r = http.get(base_link, headers=headers)
        base = BeautifulSoup(r.text, "lxml")

        items = base.find_all(class_="u-col u-col-20 u_column")

        for item in items:
            try:
                link = locator_domain + item.a["href"]
            except:
                continue
            try:
                req = http.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
            except:
                if "jack-doe/" in link:
                    link = "https://donsandbens.com/pages/location-valley-hi"
                    req = http.get(link, headers=headers)
                    base = BeautifulSoup(req.text, "lxml")
                else:
                    # Unforeseen error needs to be checked
                    raise

            location_name = base.h1.text.strip()

            raw_address = (
                base.find_all(class_="u_content_text")[1]
                .p.text.replace("Address:", "")
                .strip()
                .split("•")
            )
            street_address = raw_address[0].strip()
            city_line = raw_address[1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = ""
            location_type = ""
            phone = base.find_all(class_="u_content_text")[1].a.text
            hours_of_operation = " ".join(
                list(base.find(class_="business-hours").stripped_strings)[1:]
            ).replace("\n", "")
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

            geo = re.findall(r"2d-[0-9]{2}\.[0-9]+!3d[0-9]{2,3}\.[0-9]+", str(base))[
                0
            ].split("!")
            latitude = geo[1].split("d")[1]
            longitude = geo[0].split("d")[1]

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
