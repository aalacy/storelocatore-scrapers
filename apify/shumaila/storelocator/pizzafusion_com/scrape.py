import usaddress
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from sgselenium import SgSelenium

driver = SgSelenium().chrome()
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    links = []
    cleanr = re.compile("<.*?>")
    url = "http://pizzafusion.com/locations/"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    maindiv = soup.find("div", {"id": "usa3"})
    divs = maindiv.findAll("div")

    for div in divs:
        dets = div.findAll("div")
        for linka in dets:
            try:
                link = linka.find("a", {"class": "borderImg"})
                link = link["href"]
                link = str(link)
                if link.find("#") == -1:
                    links.append("http://pizzafusion.com" + link)
            except:
                flag = 2
    for n in range(0, len(links)):
        link = links[n]
        try:
            try:
                driver.get(link)
            except:
                pass
            soup = BeautifulSoup(driver.page_source, "html.parser")
            td = soup.find("td")
            td = str(td)
            td = re.sub(cleanr, " ", td)

            td = td.replace("\n", "|")
            td = td.replace("\r", "|")
            td = td.replace("||", "|")
        except:
            try:
                driver.get(link)
            except:
                continue
            soup = BeautifulSoup(driver.page_source, "html.parser")
            maindiv = soup.find("div", {"id": "117"})
            divs = maindiv.find("div")
            td = divs.find("p")
            td = str(td)
            td = re.sub(cleanr, " ", td)
            td = td.replace("  ", "|")
            flag = 1
        try:
            mainframe = soup.findAll("iframe")
            lat, longt = (
                str(mainframe[1]).split("sll", 1)[1].split("&", 1)[0].split(",", 1)
            )
        except:
            lat = longt = "<MISSING>"
        if flag == 1:
            start = td.find("|", 3)
            title = td[1:start]
        else:
            start = td.find(",", 0)
            title = td[2:start]
        if td.find("#") > -1:
            start = td.find("#")
            end = td.find("|", start)
            store = td[start + 1 : end]
        else:
            store = "<MISSING>"
        end = td.find("Phone")

        address = td[start:end]

        if flag == 1:
            address = address.replace("|", " ")
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
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
                or temp[1].find("LandmarkName") != -1
            ):
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        start = td.find(":", start) + 1
        end = td.find("Hours", start)
        phone = td[start:end]
        if phone.find("Fax"):
            phone = phone[0 : phone.find("Fax")]
        start = td.find("Hours")
        start = td.find(":", start) + 2
        hours = td[start : len(td)]
        start = hours.find("[")
        if start != -1:
            hours = hours[0 : start - 1]
        phone = phone.replace("\n", "")
        phone = phone.replace("|", "")
        title = title.lstrip()
        street = street.lstrip()
        city = city.lstrip()
        city = city.replace(",", "")
        pcode = pcode.lstrip()
        state = state.lstrip()
        phone = phone.lstrip()
        hours = hours.replace("|", "")
        hours = hours.replace(" &amp; ", "-")
        hours = hours.lstrip()
        hours = hours.replace("\n", "")
        pcode = pcode.replace("|", "")

        store = store.lstrip()
        flag = 0
        if len(street) < 3 and len(city) < 3:
            title = "NFA Training Center"
            street = "4000 Arlington Boulevard"
            city = "Arlington"
            state = "VA"
            pcode = "22204"

            phone = "703-302-7144"
            hours = "Monday - Friday: 10:30am - 3:00pm"
        if "1013 N. Federal Hwy." in street:
            street = street.replace(" Fort", "")
            city = "Fort " + city
        yield SgRecord(
            locator_domain="http://pizzafusion.com/",
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
