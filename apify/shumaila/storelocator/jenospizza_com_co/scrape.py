from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from sgselenium.sgselenium import SgChrome

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():

    url = "https://www.jenospizza.com.co/pizzerias"
    with SgChrome(user_agent=user_agent) as driver:

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        statelist = soup.find("ul", {"class": "areas"}).findAll("a")
        for st in statelist:
            state = st.text
            stlink = "https://www.jenospizza.com.co" + st["href"]
            driver.get(stlink)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            citylist = soup.find("ul", {"class": "cities"}).findAll("li")
            for city in citylist:
                clink = "https://www.jenospizza.com.co" + city.find("a")["href"]
                driver.get(clink)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                try:
                    loclist = soup.find("ul", {"class": "list"}).findAll("li")
                except:
                    continue
                for loc in loclist:
                    try:
                        title = loc.find("h2").text
                    except:
                        continue
                    address = loc.findAll("p", {"class": "prs"})
                    street = address[0].text
                    city = address[1].text
                    phone = loc.find("span", {"class": "pls"}).text
                    link = "https://www.jenospizza.com.co" + loc.find("a")["href"]
                    driver.get(link)
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    lat = driver.page_source.split("lat = ", 1)[1].split(";", 1)[0]
                    longt = driver.page_source.split("lng = ", 1)[1].split(";", 1)[0]
                    hourlist = soup.findAll("table")[1].findAll("td")
                    hours = ""
                    for hr in hourlist:
                        hours = hours + hr.text + " "
                    store = link.split("-")[-1]
                    yield SgRecord(
                        locator_domain="https://www.jenospizza.com.co/",
                        page_url=link,
                        location_name=title,
                        street_address=street.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=SgRecord.MISSING,
                        country_code="CO",
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
