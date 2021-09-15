from bs4 import BeautifulSoup
import re
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
    url = "https://www.extremepizza.com/store-locator/"
    cleanr = re.compile(r"<[^>]+>")
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split('{"@type": "FoodEstablishment", ')
    loclist = r.text.split('"hours"')[1:]
    for loc in loclist:
        try:
            link = loc.split('"url": "', 1)[1].split(",", 1)[0]
        except:
            break
        link = "https://www.extremepizza.com" + link.replace('"', "")

        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        address = r.text.split('"location": ', 1)[1].split("}", 1)[0]
        try:
            address = soup.find("section", {"id": "intro"}).findAll("a")[0].text.strip()
        except:
            continue
        if (
            "Coming Soon!" in soup.find("section", {"id": "intro"}).text
            or "temporarily closed"
            in soup.find("section", {"id": "intro"}).text.lower()
            or "soon!" in soup.find("section", {"id": "intro"}).text
        ):
            continue
        try:
            phone = soup.find("section", {"id": "intro"}).findAll("a")[1].text
        except:
            if (
                "Coming Soon!" in soup.find("section", {"id": "intro"}).text
                or "temporarily closed"
                in soup.find("section", {"id": "intro"}).text.lower()
                or "soon!" in soup.find("section", {"id": "intro"}).text
            ):
                continue
            else:
                phone = "<MISSING>"
        hourlist = soup.find("section", {"id": "intro"}).findAll("p")
        hours = ""
        for hr in hourlist:
            if (
                "am " in hr.text.lower()
                or "day " in hr.text.lower()
                or "am -" in hr.text.lower()
                or "pm" in hr.text.lower()
            ):

                hrnow = re.sub(cleanr, " ", str(hr)).strip()
                hours = hours + hrnow + " "
        address = address.split(", ")
        state = address[-1]
        city = address[-2]
        street = " ".join(address[0:-2])
        state, pcode = state.strip().split(" ", 1)
        title = soup.find("title").text.split(" |", 1)[0]
        lat = r.text.split('data-gmaps-lat="', 1)[1].split('"', 1)[0]
        longt = r.text.split('data-gmaps-lng="', 1)[1].split('"', 1)[0]
        if len(hours) < 3:
            hours = "<MISSING>"
        else:
            hours = hours.replace("&amp;", "&").replace(".", "")
        try:
            hours = hours.split("Try", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Thirst", 1)[0]
        except:
            pass
        try:
            hours = hours.split("PINTS", 1)[0]
        except:
            pass
        try:
            hours = hours.split("We ", 1)[0]
        except:
            pass
        if "Order Online" in phone:
            phone = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.extremepizza.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number="<MISSING>",
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=lat,
            longitude=longt.replace("\n", "").strip(),
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
