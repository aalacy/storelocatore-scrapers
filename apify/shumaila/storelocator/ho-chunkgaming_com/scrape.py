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

    pattern = re.compile(r"\s\s+")
    url = "https://ho-chunkgaming.com/"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    mainul = soup.find("nav", {"id": "menu"})
    linklist = mainul.findAll("a")
    for link in linklist:
        link = link["href"]
        try:
            r = session.get(link, headers=headers, verify=False)
        except:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        maindiv = soup.find("div", {"class": "footer-addr"}).text
        maindiv = re.sub(pattern, "\n", maindiv).lstrip().splitlines()
        title = maindiv[0]
        street = maindiv[1]
        city, state = maindiv[2].split(", ")
        state, pcode = state.lstrip().split(" ", 1)
        phone = maindiv[3]
        hours = ""
        if len(hours) < 2:            
            hourslist = soup.findAll("p", {"class": "footerp-p"})
            hours = ""
            for st in hourslist:
                if "open hours" in st.text.lower():
                    hours = hours + " " + st.text
        if len(hours) < 2:           
            hourslist = soup.findAll("b")
            hours = ""
            for st in hourslist:
                if "hours of operation" in st.text.lower():
                    hours = hours + " " + st.text
            try:
                hours = hours.split(": ", 1)[1]
            except:
                pass
            hours = hours.replace("Hours of operation:", "").strip()
            if len(hours) < 3:
                hours = ""
        if len(hours) < 2:            
            hourslist = soup.findAll("strong")
            hours = ""
            for st in hourslist:
                if (
                    ("open" in st.text.lower() and "hours" in st.text.lower())
                    or ("open" in st.text.lower() and "am " in st.text.lower())
                    or ("mon" in st.text.lower() or "tue" in st.text.lower())
                ):
                    hours = hours + " " + st.text
            if "6 MONTH POINT" in hours:
                hours = ""
        if len(hours) < 2:           
            hourslist = soup.findAll("p")
            hours = ""
            for st in hourslist:
                if ("sun " in st.text.lower() and "am " in st.text.lower()) or (
                    "fri" in st.text.lower() and "am " in st.text.lower()
                ):
                    hours = hours + " " + st.text
        if hours.find("ing yet. ") > -1:
            hours = "<MISSING>"
        else:
            hours = (
                hours.replace("â\x80\x93", "-")
                .replace("\n", "")
                .replace("Yes, ", "")
                .replace("Â", "")
            )
        try:
            hours = hours.split("NEW &", 1)[1]
        except:
            pass
        try:
            hours = hours.split("!", 1)[0]
        except:
            pass
        try:
            hours = hours.split(".", 1)[0]
        except:
            pass
        try:
            hours = hours.split("Open")[0] + " " + hours.split("Open")[1]
        except:
            pass
        hours = re.sub(pattern,' ',hours).strip()
       
        
        try:
            coord = soup.select_one("a[href*=maps]")['href']
            lat,longt = coord.split('@',1)[1].split('data',1)[0].split(',',1)
            longt = longt.split(',',1)[0]
        except:
            try:
                coord = soup.select_one("a[href*=maps]")['href']
                lat,longt = coord.split('&sll=',1)[1].split(',')
            except:
                try:
                    r.text.split('&sll=',1)[1].split('"',1)[0].split(',')
                except:
                    lat = longt = '<MISSING>'
            
      

        yield SgRecord(
            locator_domain="https://www.ho-chunkgaming.com/",
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
            longitude=longt,
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
