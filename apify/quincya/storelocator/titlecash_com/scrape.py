import re
import time

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("titlecash.com")


def fetch_data(sgw: SgWriter):

    base_link = "http://titlecash.com/find-a-location/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="store_results").find_all("a")
    locator_domain = "http://titlecash.com"

    all_links = []
    for item in items:
        link = locator_domain + item["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locs = base.table.find_all("a", target="_parent")
        for loc in locs:
            all_links.append([loc, loc.find_next("table")])

        page_links = base.find_all("a", href=re.compile(r"\?page=[0-9]+"))
        for page_link in page_links:
            req = session.get(link + page_link["href"], headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            locs = base.table.find_all("a", target="_parent")
            for loc in locs:
                all_links.append([loc, loc.find_next("table")])

    for i in all_links:
        link = locator_domain + i[0]["href"]
        log.info(link)
        req = session.get(link, headers=headers)
        try:
            base = BeautifulSoup(req.text, "lxml")
            got_page = True
        except:
            log.info("Retrying: " + link)
            time.sleep(2)
            req = session.get(link, headers=headers)
            try:
                base = BeautifulSoup(req.text, "lxml")
                got_page = True
            except:
                got_page = False

        location_name = ""

        if got_page:
            raw_data = list(
                base.find_all("table")[2].find_all("span")[-1].stripped_strings
            )
            try:
                location_type = (
                    base.find("td", colspan="2")
                    .img["src"]
                    .split("images/")[1]
                    .split("/")[0]
                )
            except:
                location_type = base.find("td", colspan="2").text
            try:
                latitude = (
                    re.findall(r"lat = [0-9]{2}\.[0-9]+", str(base))[0]
                    .split("=")[1]
                    .strip()
                )
                longitude = (
                    re.findall(r"long = -[0-9]{2,3}\.[0-9]+", str(base))[0]
                    .split("=")[1]
                    .strip()
                )
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
        else:
            raw_data = list(i[1].stripped_strings)
            location_type = (
                i[1]
                .find("td", colspan="2")
                .img["src"]
                .split("images/")[1]
                .split("/")[0]
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        street_address = raw_data[0].split("/")[0].strip()
        city_line = raw_data[1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = link.split("=")[-1]
        phone = raw_data[2].replace("Phone:", "").strip()
        hours_of_operation = raw_data[3].replace("Hours:", "").strip()

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
