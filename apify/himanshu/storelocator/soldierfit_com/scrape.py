import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://soldierfit.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }
    r = session.get(base_url + "/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find_all("div", {"class": "soldierfit_address"})
    for dt in main:
        link = base_url + dt.find("a")["href"]
        madd = list(dt.stripped_strings)
        name = madd[0] + " " + madd[1]
        address = madd[2].strip()
        ct = madd[3].replace("\xa0", " ").split(",")
        city = ct[0].strip()
        state = ct[1].strip().split(" ")[0].strip()
        zip = ct[1].strip().split(" ")[1].strip()
        phone = madd[-2].strip()
        r1 = session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if "Schedule Coming Soon!" not in soup1.text:
            hour = ""
            country = "US"
            storeno = ""
            lat = ""
            lng = ""
            for script in soup1.find_all("script"):
                if "var map_data" in script.text:
                    lt = json.loads(
                        script.text.split("var map_data =")[1].split(";")[0]
                    )
                    lat = lt["locations"][0]["lat"]
                    lng = lt["locations"][0]["lng"]
            day = soup1.find("div", {"class": "sidebar-info"}).find_all(
                "div", {"class": "sidebar-days"}
            )
            hours = soup1.find("div", {"class": "sidebar-info"}).find_all(
                "div", {"class": "sidebar-hours"}
            )
            hour = ""
            for ln in range(len(day)):
                hour += " " + day[ln].text.strip() + " " + hours[ln].text.strip()

            sgw.write_row(
                SgRecord(
                    locator_domain=base_url,
                    page_url=link,
                    location_name=name,
                    street_address=address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country,
                    store_number=storeno,
                    phone=phone,
                    location_type="",
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hour,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
