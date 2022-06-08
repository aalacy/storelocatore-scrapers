from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import usaddress

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.lawlersbarbecue.com/locations"
    jsonurl = "https://gusto-dataaccessapi.azurewebsites.net/api/v2/2099/Location"
    jsonr = session.get(jsonurl, headers=headers).json()
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select_one('li:contains("Locations")').findAll("a")[1:]
    for link in linklist:
        title = link.text
        link = link["href"]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        address = soup.text.split("Address", 1)[1].split("ORDER", 1)[0]
        try:
            address = address.split("Phone", 1)[0]
        except:
            pass
        address = address.replace("\n", " ")
        phone = (
            soup.text.split("Phone", 1)[1]
            .split("\n", 1)[1]
            .split("\n", 1)[0]
            .replace("(Main)", "")
            .strip()
        )
        hours = soup.text.split("Hours", 1)[1].split("\n", 1)[1].split("\n", 1)[0]
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
        street = street.lstrip().replace(",", "")
        city = city.lstrip().replace(",", "").strip()
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")

        lat = longt = store = "INACCESSIBLE"
        for jnow in jsonr:

            if jnow["City"] == city:

                lat = jnow["Latitude"]
                longt = jnow["Longitude"]
                store = jnow["LocationID"]
                break
        if "INACCESSIBLE" in str(store):
            try:
                store = (
                    r.text.split("https://order-online.azurewebsites.net/2099", 1)[1]
                    .split('"', 1)[0]
                    .replace("/", "")
                )
            except:
                store = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.lawlersbarbecue.com/",
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
            hours_of_operation=hours.strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
