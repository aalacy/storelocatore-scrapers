from bs4 import BeautifulSoup
import usaddress
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://behandpicked.com/handpicked-stores/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    titlelist = soup.find("div", {"class": "category-description"}).findAll("strong")
    divlist = soup.find("div", {"class": "category-description"}).text
    for i in range(0, len(titlelist) - 1):
        content = (
            divlist.split(titlelist[i].text)[1]
            .split(titlelist[i + 1].text)[0]
            .replace(":", "")
            .lstrip()
            .replace("\n", " ")
            .strip()
        )
        address = content.split("Phone", 1)[0].replace(":", "").lstrip()
        phone = (
            content.split("Phone", 1)[1].split("E-mail", 1)[0].replace(":", "").lstrip()
        )
        phone = phone.split("Hour", 1)[0].replace(":", "").lstrip()
        hours = content.split("Hours", 1)[1].split("Th", 1)[0].replace(":", "").lstrip()
        try:
            hours = hours.split("Loc", 1)[0].replace(":", "").lstrip()
        except:
            pass
        try:
            hours = hours.split("E-mail", 1)[0].strip()
        except:
            pass
        title = titlelist[i].text

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
                or temp[1].find("Occupancy") != -1
                or temp[1].find("Recipient") != -1
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
        try:
            street = street.split("located", 1)[0]
        except:
            pass
        yield SgRecord(
            locator_domain="https://behandpicked.com/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.replace(": ", "").strip(),
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
            hours_of_operation=hours.replace(": ", "").replace("&amp;", "-").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
