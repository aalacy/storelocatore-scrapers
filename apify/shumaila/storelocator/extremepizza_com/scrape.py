from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

session = SgRequests()
DOMAIN = "extremepizza.com"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"


def fetch_data():
    url = "https://www.extremepizza.com/store-locator/"
    r = session.get(url, headers=headers)
    loclist = r.text.split('{"@type": "FoodEstablishment", ')
    loclist = r.text.split('"hours"')[1:]
    for loc in loclist:
        try:
            link = loc.split('"url": "', 1)[1].split(",", 1)[0]
        except:
            break
        link = "https://www.extremepizza.com" + link.replace('"', "")
        log.info("Pull content => " + link)
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        address = r.text.split('"location": ', 1)[1].split("}", 1)[0]
        try:
            address = soup.find("section", {"id": "intro"}).findAll("a")[0].text.strip()
        except:
            continue
        check_content = soup.find("section", {"id": "intro"}).text.lower()
        if "coming" in check_content or "soon!" in check_content:
            continue
        try:
            phone = soup.find("section", {"id": "intro"}).findAll("a")[1].text
        except:
            if "coming" in check_content or "soon!" in check_content:
                continue
            else:
                phone = MISSING
        address = address.split(", ")
        state = address[-1]
        city = address[-2]
        street = " ".join(address[0:-2])
        state, pcode = state.strip().split(" ", 1)
        title = soup.find("title").text.split(" |", 1)[0]
        lat = r.text.split('data-gmaps-lat="', 1)[1].split('"', 1)[0]
        longt = r.text.split('data-gmaps-lng="', 1)[1].split('"', 1)[0]
        hoo = soup.find("section", {"id": "intro"}).find("div", {"class": "col-md-6"})
        hoo.find("h2").decompose()
        for remove_element in hoo.find_all("a"):
            remove_element.decompose()
        hoo = (
            hoo.get_text(strip=True, separator=" ")
            .replace("Dine in at 50% capacity due to current regulations", "")
            .replace("NEW HOURS", "")
        )
        hours_of_operation = re.sub(r"(Delivering to.*)|(PINTS ON.*)", "", hoo).strip()
        location_type = MISSING
        if "temporarily closed" in check_content:
            location_type = "TEMP_CLOSED"
        if "Order Online" in phone:
            phone = MISSING
        log.info("Append {} => {}".format(title, street))
        yield SgRecord(
            locator_domain="https://www.extremepizza.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=MISSING,
            phone=phone.strip(),
            location_type=location_type,
            latitude=lat,
            longitude=longt.replace("\n", "").strip(),
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
