from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgChrome

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "cookie": "visid_incap_2781737=qPvqdLRAQFaPX1z2LkIgOdINpWIAAAAAQUIPAAAAAAAu8TYPC1PbRTKk0aQ1Hrvd; incap_ses_1445_2781737=80braYXejBMBJfYGHqwNFNINpWIAAAAA5fLjYncg7A6wjE2NUPO4NA==; _ga=GA1.2.1011463266.1654984149; _gid=GA1.2.612987627.1654984149; fpestid=f1zxs1KjzpRunud90SpaQhV6RdbfS1JJ9vEro4RafIZJt2xVkLsyUzbTaCmotjH6964t9Q; incap_ses_1543_2781737=oKtLby+WNkw9xaQbdtZpFbKkpWIAAAAAytnhV8JVb8qqGDfWT16LUw==",
    "referer": "https://buckspizza.com/",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


def fetch_data():
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    with SgChrome(user_agent=user_agent) as driver:
        url = "https://buckspizza.com/locations/"
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        divlist = soup.findAll("div", {"class": "nd_options_display_table_cell"})
        for div in divlist:

            try:
                title = div.find("h4").text.strip()
            except:
                continue
            link = div.find("a")["href"]
            if "franchise" in link:
                continue
            print(link)
            driver.get(link)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            content = soup.find(
                "div", {"class": "wpb_text_column wpb_content_element"}
            ).text.strip()

            if len(content.splitlines()) < 4:
                hours = content.strip()

                content = re.sub(pattern, "\n", soup.text).strip()

                address = content.split("ADDRESS", 1)[1].strip().splitlines()
                street = address[0]
                city, state = address[1].split(", ", 1)
                state, pcode = state.split(" ", 1)
                phone = content.split("CALL NOW", 1)[1].strip().splitlines()[0]
                hours = (
                    content.split("ADDRESS", 1)[1]
                    .split("Hours: ", 1)[1]
                    .split("\n", 1)[0]
                )
            else:
                street = content.splitlines()[0]
                city, state = content.splitlines()[1].split(", ", 1)
                state, pcode = state.split(" ", 1)
                phone = content.splitlines()[2]

                if "temporarily close" in content.lower():
                    hours = "Temporarily Closed"
                else:
                    hours = content.split("Hours", 1)[1].split("\n", 1)[1]
            try:
                hours = hours.split("$", 1)[0]
                hours = hours.split("For", 1)[0]
            except:
                pass
            try:
                longt, lat = (
                    soup.find("iframe")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d", 1)
                )
            except:
                lat = longt = "<MISSING>"
            yield SgRecord(
                locator_domain="https://buckspizza.com/",
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
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours.replace("\n", " ").strip(),
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
