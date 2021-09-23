from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.centurypa.com/"
    country_code = "US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    r = session.get("https://www.centurypa.com/communities/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for statelinks in soup.find("div", {"id": "stateListContain"}).find_all("a"):
        r1 = session.get(
            "https://www.centurypa.com" + statelinks["href"], headers=headers
        )
        soup1 = BeautifulSoup(r1.text, "lxml")
        for loc_contain in soup1.find("div", {"id": "locationContain"}).find_all(
            "div", class_="locationDeets"
        ):
            location_name = loc_contain.find("h2").text.strip()
            page_url = "https://www.centurypa.com" + loc_contain.find("h2").a["href"]
            phone = (
                loc_contain.find("p", class_="lrgPhone")
                .text.replace("Phone:", "")
                .strip()
            )
            address = list(
                loc_contain.find("p", class_="lrgPhone").find_next("p").stripped_strings
            )
            street_address = " ".join(address[:-1]).strip()
            city = address[-1].split(",")[0].strip()
            state = address[-1].split(",")[-1].split()[0].strip()
            zipp = address[-1].split(",")[-1].split()[-1].strip()
            r3 = session.get(page_url, headers=headers)
            soup3 = BeautifulSoup(r3.text, "lxml")

            try:
                contact_link = (
                    "https://www.centurypa.com"
                    + soup3.find("div", class_="contactContain").find(
                        "a", class_="ghostBtn"
                    )["href"]
                )
                r4 = session.get(contact_link, headers=headers)
                soup4 = BeautifulSoup(r4.text, "lxml")
                longitude = (
                    soup4.find("div", {"id": "map"})
                    .find("iframe")["src"]
                    .split("!2d")[1]
                    .split("!3d")[0]
                )
                latitude = (
                    soup4.find("div", {"id": "map"})
                    .find("iframe")["src"]
                    .split("!2d")[1]
                    .split("!3d")[1]
                    .split("!")[0]
                )
            except:
                latitude = ""
                longitude = ""
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
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
