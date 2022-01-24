from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.fhcn.org/locations"
    r = session.get(url, headers=headers)
    r.encoding = "utf-8-sig"
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "location_detail"})
    for loc in loclist:
        title = loc.find("div", {"class": "location_detail_title"}).text.strip()
        if "mobile " in title.lower():
            continue
        try:
            phone = (
                loc.find("div", {"class": "phone-wrapper"})
                .text.replace("Phone", "")
                .strip()
            )
        except:
            phone = "<MISSING>"
        address = loc.find("div", {"class": "address-wrapper"})
        address = re.sub(cleanr, "\n", str(address))
        address = (
            re.sub(pattern, "\n", str(address))
            .replace("Address", "")
            .replace("\n", " ")
            .strip()
        )
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
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")

        ltype = loc.find("div", {"class": "location-services"}).text.strip()
        hours = (
            loc.find("div", {"class": "hours-wrapper"})
            .text.replace("Hours", "")
            .strip()
        )
        title = (
            str(title.encode(encoding="ascii", errors="replace"))
            .replace("?", " ")
            .replace("b'", "")
            .strip()
            .replace("'", "")
        )
        try:
            hours = hours.split("Medical", 1)[1].strip().split("Dental", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Chiropractic", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Walk", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Pharmacy", 1)[0]
        except:
            pass
        if "call" in hours:
            hours = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.fhcn.org/",
            page_url=SgRecord.MISSING,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours.replace("pm", "pm ")
            .replace("PM", "PM ")
            .replace("day", "day ")
            .replace("Services", "")
            .replace("\n", "")
            .strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
