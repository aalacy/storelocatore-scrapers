from bs4 import BeautifulSoup as bs
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog
import json

session = SgRequests()
DOMAIN = "extremepizza.com"
BASE_URL = "https://www.extremepizza.com"
LOCATION_URL = "https://www.extremepizza.com/store-locator/"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    soup = pull_content(LOCATION_URL)
    loclist = json.loads(soup.find("script", {"type": "application/ld+json"}).string)
    for loc in loclist["subOrganization"][1:]:
        link = loc["url"]
        log.info("Pull content => " + link)
        r = session.get(link, headers=HEADERS)
        content = bs(r.text, "lxml")
        address = r.text.split('"location": ', 1)[1].split("}", 1)[0]
        try:
            address = (
                content.find("section", {"id": "intro"}).findAll("a")[0].text.strip()
            )
        except:
            continue
        check_content = content.find("section", {"id": "intro"}).text.lower()
        if (
            "temporarily closed" not in check_content
            and "coming" in check_content
            or "soon!" in check_content
        ):
            continue
        try:
            phone = content.find("section", {"id": "intro"}).findAll("a")[1].text
        except:
            if (
                "temporarily closed" not in check_content
                and "coming" in check_content
                or "soon!" in check_content
            ):
                continue
            else:
                phone = MISSING
        address = address.split(", ")
        state = address[-1]
        city = address[-2]
        street = " ".join(address[0:-2])
        state, pcode = state.strip().split(" ", 1)
        title = content.find("title").text.split(" |", 1)[0]
        lat = r.text.split('data-gmaps-lat="', 1)[1].split('"', 1)[0]
        longt = r.text.split('data-gmaps-lng="', 1)[1].split('"', 1)[0]
        hoo = content.find("section", {"id": "intro"}).find(
            "div", {"class": "col-md-6"}
        )
        hoo.find("h2").decompose()
        for remove_element in hoo.find_all("a"):
            remove_element.decompose()
        hoo = (
            hoo.get_text(strip=True, separator=" ")
            .replace("Dine in at 50% capacity due to current regulations", "")
            .replace("NEW HOURS", "")
        )
        hours_of_operation = re.sub(
            r"(Delivering to.*)|(PINTS ON.*)|(For orders.*)", "", hoo
        ).strip()
        location_type = MISSING
        if "temporarily closed" in check_content:
            location_type = "TEMP_CLOSED"
        if "Order Online" in phone:
            phone = MISSING
        log.info("Append {} => {}".format(title, street))
        yield SgRecord(
            locator_domain=DOMAIN,
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
