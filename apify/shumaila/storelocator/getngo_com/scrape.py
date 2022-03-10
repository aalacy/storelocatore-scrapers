from bs4 import BeautifulSoup
import usaddress
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.getngo.com/locations/"

    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=locations]")
    for link in linklist:
        link = link["href"]
        if "getngo" not in link:
            continue
        link = "https://www.getngo.com" + link
        store = link.split("/getngo", 1)[1].split("/", 1)[0]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h2").text
        address = soup.find("h3").text
        phone = (
            soup.select_one('p:contains("Phone")').text.replace("Phone: ", "").strip()
        )
        hours = (
            soup.select_one('p:contains("Hours")').text.replace("Hours: ", "").strip()
        )
        lat, longt = r.text.split("maps.LatLng(", 1)[1].split(")", 1)[0].split(", ", 1)
        address = usaddress.parse(address)
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
        if len(city) < 3 and "Sioux Falls" in street:
            city = "Sioux Falls"
            street = street.replace("Sioux Falls", "")
        street = street.lstrip().replace(",", "")
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")

        yield SgRecord(
            locator_domain="https://www.getngo.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
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
