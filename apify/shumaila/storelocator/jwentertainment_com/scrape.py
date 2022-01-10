import usaddress
from bs4 import BeautifulSoup
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

    url = "https://jwentertainment.com/locations/#"
    page = session.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    repolist = soup.findAll("div", {"class": "location_image mb-2"})
    for div in repolist:
        store = div["id"]
        store = store.replace("location_div_", "")
        link = div.find("a")
        link = link["href"]
        page = session.get(link, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.find("section", {"class": "event_locations"})
        title = maindiv.find("h4").text
        address = maindiv.find("p", {"class": "white mb-4"}).text
        address = usaddress.parse(address)
        m = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while m < len(address):
            temp = address[m]
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
            m += 1
        city = city.lstrip()
        street = street.lstrip()
        state = state.lstrip()
        pcode = pcode.lstrip()
        contacts = maindiv.findAll("a", {"class": "learn_more_btn w-100"})
        phone = contacts[0]["href"]
        lat, longt = (
            contacts[1]["href"].split("@", 1)[1].split("data", 1)[0].split(",", 1)
        )
        longt = longt.split(",", 1)[0]
        hours = (
            maindiv.find("table", {"table table-striped timetable_locations"})
            .text.replace("â€“", " - ")
            .replace("am", " am ")
            .replace("pm", " pm ")
            .replace("day", "day : ")
        )
        phone = phone.replace("tel:", "")
        title = title.replace(" TRAMPOLINE PARK", "")
        city = city.replace(",", "")
        hours = hours.encode("ascii", "ignore").decode("ascii")
        yield SgRecord(
            locator_domain="https://jwentertainment.com/",
            page_url=link,
            location_name=title,
            street_address=street.replace(",", "").strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.replace("\n", " ").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
