from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://sunrisedental.com/page-sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select('loc:contains("near-me")')
    divlist = divlist + soup.select('loc:contains("top")')
    for div in divlist:
        link = div.text
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            title = soup.find("strong").text
        except:
            title = (
                soup.find("title")
                .text.split("-", 1)[0]
                .replace("Dentist Near Me ", "Sunrise Dental ")
                .strip()
            )
        try:
            title = title.split("offers", 1)[0]
        except:
            pass
        if "COMING SOON" in title:
            continue
        hours = soup.text.split("Monday", 1)[1]
        try:
            phone = soup.find("small").text

            hours = "Monday" + hours.split("Your", 1)[0].replace("pm", "pm ")
        except:
            try:
                phone = (
                    soup.find("div", {"class": "elementor-text-editor"})
                    .find("h2")
                    .text.split("\n", 1)[0]
                )
            except:
                phone = "360-639-3355"
            if len(phone) < 3:
                phone = soup.findAll("h2", {"class": "elementor-heading-title"})[
                    2
                ].text.strip()
            hours = "Monday" + hours.split("Dental", 1)[0]
        address = (
            soup.findAll("iframe")[-1]["title"].replace(" United States", "").strip()
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
        hours = re.sub(pattern, " ", hours).strip()
        hours = (
            str(hours.encode(encoding="ascii", errors="replace"))
            .replace("?", "-")
            .replace("b'", "")
            .replace("'", "")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://sunrisedental.com/",
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
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
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
