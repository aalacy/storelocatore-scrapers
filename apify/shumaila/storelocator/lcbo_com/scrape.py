from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
headers = {
    "traceparent": "00-5fa2285db0a256ad2e16522658a8b970-4df622a25adc21f5-01",
    "tracestate": "1322840@nr=0-1-3202131-1028008692-4df622a25adc21f5----1650407796333",
    "x-newrelic-id": "VwQHU1dQCRAJU1NUAgMEUFQ=",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

MISSING = SgRecord.MISSING


def fetch_data():
    cleanr = re.compile(r"<[^>]+>")

    pattern = re.compile(r"\s\s+")
    page = 1
    dataobj = {
        "lat": "0",
        "lng": "0",
        "inventoryFilter": "false",
        "pdpCheck": "true",
        "favouriteFilter": "false",
        "radius": "0",
        "sku": "0",
        "product": "0",
        "category": "0",
        "sortByDistance": "false",
    }
    while page < 69:
        url = "https://www.lcbo.com/en/amlocator/index/ajax/?p=" + str(page)
        loclist = session.post(url, headers=headers, data=dataobj).json()

        hourlist = BeautifulSoup(loclist["block"], "html.parser").findAll(
            "div", {"class": "amlocator-schedule-container"}
        )
        loclist = loclist["items"]
        page = page + 1
        for i in range(0, len(loclist)):
            loc = loclist[i]
            hours = hourlist[i].text
            hours = hours.split(" today ", 1)[1].strip()

            store = loc["id"]
            lat = loc["lat"]
            longt = loc["lng"]

            soup = BeautifulSoup(loc["popup_html"], "html.parser")

            title = soup.find("h3").text
            link = soup.find("a")["href"]
            try:
                phone = soup.find("div", {"class": "amlocator-phone-number"}).text
            except:
                phone = "<MISSING>"
            address = str(soup.find("div", {"class": "amlocator-info-popup"}))

            address = re.sub(cleanr, " ", address)
            address = re.sub(pattern, " ", address).replace(" address 2:", " ").strip()

            raw_address = address
            r = session.get(link, headers=headers)
            city = (
                BeautifulSoup(r.text, "html.parser")
                .find("span", {"class": "amlocator-text-city"})
                .text.replace(",", "")
                .strip()
            )

            street, state = address.split(" " + city + " ,", 1)

            state, pcode = state.strip().split(" ", 1)

            yield SgRecord(
                locator_domain="https://www.lcbo.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="CA",
                store_number=str(store),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
                raw_address=raw_address,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
