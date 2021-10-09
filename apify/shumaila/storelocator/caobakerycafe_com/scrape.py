import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgSelenium

driver = SgSelenium().chrome()
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
session = SgRequests()
headers = {
    "authority": "www.caobakerycafe.com",
    "method": "GET",
    "path": "/coral-way-menu",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "cookie": "Popmenu-Token=eyJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoiZWZhNjYxMzAtOTk0NS00NjMwLTgxNDItY2UyZWI0N2I2OTRmIiwidG9rZW5fdmVyc2lvbiI6IlYyIiwidXNlcl9pZCI6bnVsbH0.Pzq09Rv9wvQeGLjHYVutGbjz14TUwfEVDbDKg-Nzlso; __cfruid=0a3aa509f1272cf501fe00014e7d887c92fd46f9-1633770495; _sp_ses.1e9a=*; _ga=GA1.2.1827107400.1633770504; _gid=GA1.2.1629147367.1633770504; _sp_id.1e9a=c8ed98ca-36e7-4759-9265-9038dc8fe010.1633770504.1.1633771724.1633770504.c5bbfae5-e59a-460c-8f53-b58c5f0f8656; _gat_popmenuTracker=1; __cf_bm=TV8euk7iHo4MlFXnaoOexKZypBwNDiCQfSbcZOL9x7w-1633771725-0-AWx3F0rmcqZHHhnhjgvuI9grIdXjAwVnRNe0Pyw3RuYGIYZp1cOzlVd6lBgiNvxXxDnoyTm1iqxXi3Lpz3vB2RU=",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def fetch_data():

    url = "https://www.caobakerycafe.com/locations"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    contentlist = soup.findAll("div", {"class": "pm-location"})
    loclist = driver.page_source.split('<script id="popmenu-apollo-state">', 1)[
        1
    ].split("</script>", 1)[0]
    loclist = loclist.split("RestaurantLocation:")[1:]
    p = 0
    for loc in loclist:
        loc = loc.split("{", 1)[1].split(',"scheduledDeliveryTimeSlots"', 1)[0]
        loc = "{" + loc + "}"
        try:
            loc = json.loads(loc)
        except:
            break
        store = loc["id"]
        phone = loc["displayPhone"]
        street, city, state = loc["fullAddress"].split(", ")
        state, pcode = state.strip().split(" ", 1)
        ccode = loc["country"]
        lat = loc["lat"]
        longt = loc["lng"]

        title = contentlist[p].find("h4").text
        link = (
            "https://www.caobakerycafe.com"
            + contentlist[p].find("a", {"class": "details-button"})["href"]
        )
        hours = (
            contentlist[p]
            .find("div", {"class": "hours"})
            .text.replace("pm", "pm ")
            .strip()
        )
        p += 1

        hours = hours.encode("ascii", "ignore").decode("ascii")

        yield SgRecord(
            locator_domain="https://www.caobakerycafe.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
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
