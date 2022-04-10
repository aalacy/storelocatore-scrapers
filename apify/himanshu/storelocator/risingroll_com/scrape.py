import json
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
    with SgChrome(user_agent=user_agent) as driver:
        url = "https://www.risingroll.com/locations"
        driver.get(url)
        divlist = driver.page_source.split('<script type="application/ld+json">')[1:]
        divlist = driver.page_source.split(',"RestaurantLocation:')[1:]
        for div in divlist:

            div = div.split(":", 1)[1]
            try:
                div = json.loads(div)
            except:
                try:
                    div = div.split('},"CustomPage:', 1)[0] + "}"
                    div = json.loads(div)
                except:
                    div = div.split('},"Dish:', 1)[0] + "}"
                    div = json.loads(div)
            store = div["id"]
            city = div["city"]
            title = div["name"]

            state = div["state"]
            try:
                phone = div["displayPhone"].strip()
            except:
                phone = "<MISSING>"
            lat = div["lat"]
            longt = div["lng"]
            pcode = div["postalCode"]
            try:
                link = "https://www.risingroll.com/menu-" + div["slug"].strip()
            except:
                link = "<MISSING>"
            state = div["stateName"]
            street = div["streetAddress"].replace("\n", " ").strip()

            try:
                hourslist = div["schemaHours"]

                timestr = hourslist[0].split(" ", 1)[1]

                start, endstr = timestr.split("-")
                close = int(endstr.split(":", 1)[0])
                if close > 12:
                    close = close - 12
                hours = (
                    hourslist[0].split(" ", 1)[0]
                    + " - "
                    + hourslist[-1].split(" ", 1)[0]
                    + " : "
                    + start
                    + " am - "
                    + str(close)
                    + ":"
                    + endstr.split(":", 1)[1]
                    + " pm "
                )
                if "Sa " not in hours:
                    hours = hours + "Sat - Sun : Closed"
                else:
                    hours = hours + "Sun : Closed"
            except:
                hours = "<MISSING>"
            ltype = "<MISSING>"
            try:
                if "Coming Soon" in div["customLocationContent"]:
                    ltype = "Coming Soon"
            except:
                pass
            yield SgRecord(
                locator_domain="https://www.risingroll.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(store),
                phone=phone.strip(),
                location_type=ltype,
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
