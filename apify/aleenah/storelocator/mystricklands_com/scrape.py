from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://www.mystricklands.com/pages-sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    checklist = []
    linklist = soup.findAll("loc")
    for link in linklist:
        link = link.text
        if (len(link.split("-m")[-1])) == 0:
            pass
        else:
            continue
        link = link[0 : len(link) - 2]
        if "cuyahoga-falls" in link or "streetsboro" in link:
            link = link + "-1"
        if link in checklist or "-dippers" in link:
            continue
        checklist.append(link)
        r = session.get(link, headers=headers)

        ltype = "<MISSING>"
        soup = BeautifulSoup(r.text, "html.parser")
        content = re.sub(pattern, "\n", soup.text)

        try:
            address = (
                content.split(" Menu", 1)[1]
                .split("Open Daily", 1)[0]
                .replace("\n", " ")
                .strip()
            )
        except:
            if "relocating.png" in r.text:
                continue
            else:
                pass
        if "Phone" in address:
            address = (
                content.split(" Menu", 1)[1]
                .split(".", 1)[1]
                .split("Phone", 1)[0]
                .replace("\n", " ")
                .strip()
            )
        elif "Webmaster" in address:
            address = content.split("!", 1)[1].split("\n", 1)[0]
        title = soup.find("h2").text.strip()
        try:
            phone = soup.text.split("Phone:", 1)[1].split("\n", 1)[0].strip()
        except:
            phone = "<MISSING>"
        try:
            phone = phone.split(" Flavor", 1)[0]
        except:
            pass
        try:
            hours = soup.text.split("Hours", 1)[1]
            hours = (
                hours.replace("\n", " ").replace(": ", "").strip().split("daily", 1)[0]
            )
        except:
            try:
                hours = (
                    soup.text.lower()
                    .split("daily", 1)[1]
                    .split("\n", 1)[0]
                    .replace(": ", "")
                    .strip()
                )
                if len(hours) < 3:
                    hours = (
                        soup.text.lower()
                        .split("daily", 1)[1]
                        .split("\n", 1)[1]
                        .split("\n", 1)[0]
                        .replace(": ", "")
                        .strip()
                    )
            except:
                hours = "<MISSING>"
        if len(address) < 4:
            address = soup.find("div", {"id": "comp-j3w0h1ql"}).text.split("\n", 1)[0]
        address = usaddress.parse(address.strip())

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

        yield SgRecord(
            locator_domain="https://www.mystricklands.com",
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
