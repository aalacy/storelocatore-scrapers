from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data():

    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    }

    base_url = "https://www.dfs.co.uk/"
    r = session.get("https://www.dfs.co.uk/store-directory", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all("a", {"class": "btn-xl button primary moreBttonRight"}):
        page_url = link["href"]

        if "/stratford" in page_url:
            page_url = "https://www.dfs.co.uk/StoreDetailView?distanceInMiles=0.3019486311693204&catalogId=10101&storeLatitude=51.5442&storeLongitude=-0.01327&stores=stores&searchResultLatitude=51.5471806&searchResultLongitude=-0.0081304&storeName=stratford&storeId=10202&distanceInKilometers=0.4859392178805588&langId=-1&stlocId=63501"
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("h3", {"class": "legalName"}).text.strip()
        street_address = re.sub(
            r"\s+", " ", soup1.find("span", {"itemprop": "streetAddress"}).text
        )
        try:
            city = soup1.find("span", {"itemprop": "addressLocality"}).text.strip()
        except:
            city = "<MISSING>"
        state = soup1.find("span", {"itemprop": "addressRegion"}).text.strip()
        zipp = soup1.find("span", {"itemprop": "postalCode"}).text.strip()
        phone = re.sub(
            r"\s+",
            " ",
            soup1.find("p", {"class": "contact"}).find("a")["href"].split("tel:")[-1],
        )
        store_number = soup1.find("input", {"name": "stLocId"})["value"]
        try:
            temp, city = city.split(",")
            city = city.strip()
            street_address = street_address + " " + temp
        except:
            pass
        try:
            state, zipp = zipp.split(",")
        except:
            pass
        latitude = r1.text.split("myStoreLat = ")[1].split("+")[0].strip()
        longitude = r1.text.split("myStoreLon = ")[1].split("+")[0].strip()
        hours_of_operation = re.sub(
            r"\s+",
            " ",
            " ".join(
                list(soup1.find("div", {"class": "KstoreOpening"}).stripped_strings)
            ),
        )

        yield SgRecord(
            locator_domain=base_url,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.replace(city, ""),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zipp,
            country_code="UK",
            store_number=store_number,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(latitude),
            longitude=str(longitude),
            hours_of_operation=hours_of_operation,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
