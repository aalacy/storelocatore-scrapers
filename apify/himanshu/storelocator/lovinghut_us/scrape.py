from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://lovinghut.us/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    states = soup.find_all("ul", {"class": "sub-menu"})
    for i in states:
        for j in i.find_all("li"):
            link = j.find("a")["href"]
            if link == "#":
                continue
            else:
                r1 = session.get(link, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                if "OPEN SOON" in soup1.find(id="main").text.upper():
                    continue
                location_name = soup1.h1.text
                temp_add = list(
                    soup1.find("address", {"class": "text-white"}).stripped_strings
                )
                street_address = temp_add[0]
                city = temp_add[1].split(",")[0]
                state = temp_add[1].split(" ")[-2]
                zipp = temp_add[1].split(" ")[-1]
                phone = temp_add[2]
                hoo = list(
                    soup1.find(
                        "div", {"class": "textwidget openhours"}
                    ).stripped_strings
                )
                hours_of_operation = (
                    " ".join(hoo)
                    .replace("TEMPORARY NEW HOURS : ", "")
                    .split("Last")[0]
                    .split("Kitchen")[0]
                    .split("Brunch")[0]
                    .strip()
                )

                sgw.write_row(
                    SgRecord(
                        locator_domain=base_url,
                        page_url=link,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code="US",
                        store_number="<MISSING>",
                        phone=phone,
                        location_type="<MISSING>",
                        latitude="<MISSING>",
                        longitude="<MISSING>",
                        hours_of_operation=hours_of_operation,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
