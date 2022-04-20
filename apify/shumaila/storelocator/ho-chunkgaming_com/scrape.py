import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "ho-chunkgaming_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://ho-chunkgaming.com/"
MISSING = SgRecord.MISSING


def fetch_data():

    pattern = re.compile(r"\s\s+")
    url = "https://ho-chunkgaming.com/"
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
        log.info(link)
        soup = BeautifulSoup(r.text, "html.parser")
        address = (
            soup.find("div", {"class": "footer-addr"})
            .get_text(separator="|", strip=True)
            .split("|")
        )
        title = address[0]
        phone = address[3]
        street = address[1].split("\n")
        street = " ".join(x.strip() for x in street)
        address = address[2].split(",")
        city = address[0]
        address = address[1].split()
        state = address[0]
        pcode = address[1]
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
            hours = hours.split("NEW ", 1)[1]
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
        hours = re.sub(pattern, " ", hours).strip()

        try:
            coord = soup.select_one("a[href*=maps]")["href"]
            lat, longt = coord.split("@", 1)[1].split("data", 1)[0].split(",", 1)
            longt = longt.split(",", 1)[0]
        except:
            try:
                coord = soup.select_one("a[href*=maps]")["href"]
                lat, longt = coord.split("&sll=", 1)[1].split(",")
            except:
                try:
                    lat, longt = r.text.split("&sll=", 1)[1].split('"', 1)[0].split(",")
                except:
                    lat, longt = (
                        soup.select_one("a[href*=geo]")["href"]
                        .split("geo:")[1]
                        .split(",")
                    )
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
