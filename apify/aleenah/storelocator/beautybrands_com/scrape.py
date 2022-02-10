import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("beautybrands_com")


def write_output(data):
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    }

    res = session.get(
        "https://www.beautybrands.com/store-locator/all-stores.do", headers=headers
    )
    soup = BeautifulSoup(res.text, "html.parser")
    sa = soup.find_all("div", {"class": "eslStore ml-storelocator-headertext"})
    for a in sa:
        a = a.find("a")
        url = "https://www.beautybrands.com/" + a.get("href")
        logger.info(url)
        res = session.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        ph = soup.find("div", {"class": "eslPhone"}).text.strip()
        if ph == "":
            ph = "<MISSING>"
        tim = (
            soup.find("span", {"class": "ml-storelocator-hours-details"})
            .text.replace("Book Appointment", "")
            .replace("Call", "")
            .split("IMPORTANT INFORMATION")[0]
            .strip()
        )
        if tim == "":
            tim = "<MISSING>"
        strsoup = str(soup)

        yield SgRecord(
            locator_domain="https://www.beautybrands.com",
            page_url=url,
            location_name=soup.find("div", {"class": "eslStore"}).text,
            street_address=soup.find("div", {"class": "eslAddress1"}).text
            + " "
            + soup.find("div", {"class": "eslAddress2"}).text,
            city=soup.find("span", {"class": "eslCity"}).text.replace(",", ""),
            state=soup.find("span", {"class": "eslStateCode"}).text.strip(),
            zip_postal=soup.find("span", {"class": "eslPostalCode"}).text,
            country_code="US",
            store_number=re.findall(r'"code":"([\d]+)","address"', strsoup)[0],
            phone=ph,
            location_type="<MISSING>",
            latitude=re.findall(r'"latitude":(-?[\d\.]+)', strsoup)[0],
            longitude=re.findall(r'"longitude":(-?[\d\.]+)', strsoup)[0],
            hours_of_operation=tim.replace("Sunday", " Sunday").strip(),
        )


def scrape():
    write_output(fetch_data())


scrape()
