from bs4 import BeautifulSoup
import usaddress
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from sgselenium.sgselenium import SgChrome

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://greendragon.com/location-sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "xml")
    linklist = soup.findAll("loc")

    with SgChrome(user_agent=user_agent) as driver:
        for link in linklist:

            link = link.text
            driver.get(link)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            title = soup.find("h1").text
            try:
                address = (
                    soup.find("div", {"class": "location-details"}).find("small").text
                )
                phone = soup.find("span", {"itemprop": "telephone"}).text
                lat = (
                    driver.page_source.split('"GeoCoordinates",', 1)[1]
                    .split('"latitude": "', 1)[1]
                    .split('"', 1)[0]
                )
                longt = (
                    driver.page_source.split('"GeoCoordinates",', 1)[1]
                    .split('"longitude": "', 1)[1]
                    .split('"', 1)[0]
                )

                address = usaddress.parse(address)
                ltype = "Store"
                i = 0
                street = ""
                city = ""
                state = ""
                pcode = ""
                while i < len(address):
                    temp = address[i]
                    if (
                        temp[1].find("Address") != -1
                        or temp[1].find("Street") != -1
                        or temp[1].find("Recipient") != -1
                        or temp[1].find("Occupancy") != -1
                        or temp[1].find("BuildingName") != -1
                        or temp[1].find("USPSBoxType") != -1
                        or temp[1].find("USPSBoxID") != -1
                    ):
                        street = street + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        pcode = pcode + " " + temp[0]
                    i += 1
                street = street.lstrip().replace(",", "")
                city = city.lstrip().replace(",", "")
                state = state.lstrip().replace(",", "")
                pcode = pcode.lstrip().replace(",", "")
            except:
                street = city = state = pcode = phone = lat = longt = "<MISSING>"
                ltype = "Delivery Only"
            hours = (
                soup.find("div", {"class": "location-details"})
                .findAll("p")[-1]
                .text.strip()
            )
            try:
                hours = hours.split("\n", 1)[0]
            except:
                pass
            try:
                hours = hours.split("ay: ", 1)[1]
            except:
                pass
            yield SgRecord(
                locator_domain="https://greendragon.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=ltype,
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
