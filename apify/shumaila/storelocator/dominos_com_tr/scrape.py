import json
import unidecode
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

from sgselenium.sgselenium import SgChrome

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():

    with SgChrome(user_agent=user_agent) as driver:
        url = "https://www.dominos.com.tr/"
        driver.get(url)

        divlist = driver.page_source.split('"stores":[')[1:]
        for div in divlist:
            div = div.split("]}", 1)[0]
            div = "[" + div + "]"

            if '"cityStores":[]' in div:
                break
            div = json.loads(div)
            for store in div:
                store = store["id"]
                apiurl = (
                    "https://fe.dominos.com.tr/api/store/detail?LocationCode="
                    + str(store)
                    + "&IncludeCity=true&IncludeCounties=true&IncludeStoreLiveTimes=true&IncludeDeliveryArea=true"
                )

                driver.get(apiurl)
                loc = driver.page_source.split("{", 1)[1].split("<", 1)[0]
                loc = "{" + loc
                loc = json.loads(loc)

                hours = loc["availableFrom"] + "-" + loc["availableUntil"]
                title = loc["name"]
                street = loc["address"]
                street = unidecode.unidecode(street)

                phone = loc["phone"]
                try:
                    longt = loc["longitude"]
                except:
                    longt = "<MISSING>"
                try:
                    lat = loc["lattitude"]
                except:
                    lat = "<MISSING>"
                city = loc["city"]["name"]
                city = unidecode.unidecode(city)
                title = unidecode.unidecode(title)

                street = (
                    street.replace(" " + city, "")
                    .replace(" / " + city, "")
                    .replace("/" + city, "")
                    .replace("-" + city, "")
                    .replace(" - " + city, "")
                )
                yield SgRecord(
                    locator_domain="https://fe.dominos.com.tr/",
                    page_url=SgRecord.MISSING,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=SgRecord.MISSING,
                    zip_postal=SgRecord.MISSING,
                    country_code="TR",
                    store_number=str(store),
                    phone=SgRecord.MISSING,
                    location_type=SgRecord.MISSING,
                    latitude=str(lat),
                    longitude=str(longt),
                    hours_of_operation=hours,
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
