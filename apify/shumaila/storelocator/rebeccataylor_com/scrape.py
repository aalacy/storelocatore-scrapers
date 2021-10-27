from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://www.rebeccataylor.com/our-stores/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    store_list = soup.select('a:contains("Details")')
    for st in store_list:
        if "https://www.rebeccataylor.com" in st["href"]:
            link = st["href"]
        else:
            link = "https://www.rebeccataylor.com" + st["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h2", {"class": "card-title"}).text
        try:
            address = (
                soup.find("div", {"class": "directions"}).text.strip().split("\n", 1)[0]
            )
        except:
            continue
        try:
            lat, longt = (
                soup.find("div", {"class": "directions"})
                .find("a")["href"]
                .split("@", 1)[1]
                .split("data", 1)[0]
                .split(",", 1)
            )
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        try:
            hours = soup.find("div", {"class": "card-info"}).find("ul").text
            hours, phone = hours.split("TEL", 1)
            hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()
            phone = phone.split("\n", 1)[0].split(": ", 1)[1]
        except:
            continue
        ltype = "Store"
        if "Outlet" in title:
            ltype = "Outlet"
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
        yield SgRecord(
            locator_domain="https://www.rebeccataylor.com/",
            page_url=link,
            location_name=title,
            street_address=street.replace(",", "").strip(),
            city=city.replace(",", "").strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
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
