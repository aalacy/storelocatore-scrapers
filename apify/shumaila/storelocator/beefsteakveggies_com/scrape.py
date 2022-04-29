from bs4 import BeautifulSoup
import usaddress
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "http://beefsteakveggies.com/where-we-are/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("a", {"class": "card__btn"})
    for link in linklist:
        link = "https://www.beefsteakveggies.com" + link["href"]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        maindiv = soup.find("section", {"id": "intro"})
        title = maindiv.find("h2").text
        address = maindiv.find("a", {"data-bb-track-category": "Address"}).text
        address = address.lstrip()
        address = address.replace("\n", "")
        address = address.replace(",", " ")
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
        street = street.lstrip()
        street = street.replace(",", "")
        city = city.lstrip()
        city = city.replace(",", "")
        state = state.lstrip()
        state = state.replace(",", "")
        pcode = pcode.lstrip()
        pcode = pcode.replace(",", "")

        try:
            phone = maindiv.find("a", {"data-bb-track-category": "Phone Number"}).text
        except:
            phone = "<MISSING>"
        coords = soup.find("div", {"class": "gmaps"})
        lat = coords["data-gmaps-lat"]
        longt = coords["data-gmaps-lng"]
        hours = soup.find("div", {"class": "col-md-6"})
        if "Temporarily Closed" in soup.text:
            hours = "Temporarily Closed"
        else:
            try:
                hours = (
                    "MONDAY - FRIDAY "
                    + soup.text.split("MONDAY - FRIDAY", 1)[1].split("Think", 1)[0]
                )
            except:
                hours = "<MISSING>"
        try:
            hours = hours.split("DOWNLOA", 1)[0]
        except:
            pass
        yield SgRecord(
            locator_domain="http://beefsteakveggies.com",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
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
