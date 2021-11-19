from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://lolasmexicancuisine.com/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    k = soup.find_all(
        class_="relative menu-item menu-item-type-post_type menu-item-object-locations"
    )

    for i in k:
        link = i.a["href"]
        r = session.get(link, headers=headers)
        soup1 = BeautifulSoup(r.text, "lxml")
        v = soup1.find("div", {"class": "col-span-12 md:col-span-6"})
        name = list(v.stripped_strings)[0].replace("Address", "")
        st = list(v.stripped_strings)[1].strip()
        city = list(v.stripped_strings)[2].split(",")[0].strip()
        state = list(v.stripped_strings)[2].split(",")[1].strip()
        zip1 = list(v.stripped_strings)[2].split(",")[-1].strip()
        phone = list(v.stripped_strings)[3]
        hours = " ".join(list(v.stripped_strings)[4:])
        store_number = ""
        location_type = ""
        latitude = ""
        longitude = ""

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=link,
                location_name=name,
                street_address=st,
                city=city,
                state=state,
                zip_postal=zip1,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
