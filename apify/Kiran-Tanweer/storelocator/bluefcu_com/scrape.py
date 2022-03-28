from bs4 import BeautifulSoup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgChrome
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():

    url = "https://www.bluefcu.com/sitemaps-1-section-locations-1-sitemap.xml"
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        linklist = soup.select("a[href*=locations]")
        for link in linklist:
            link = link["href"]
            driver.get(link)
            content1 = driver.page_source.split(
                '<script type="application/ld+json">', 1
            )[1].split("</script>", 1)[0]
            content1 = json.loads(content1)
            content = content1["@graph"][0]
            address = content["address"]
            ccode = address["addressCountry"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            pcode = address["postalCode"]
            street = address["streetAddress"]
            title = content["name"]
            phone = content["telephone"]

            hourslist = content["openingHoursSpecification"]
            hours = ""
            for hr in hourslist:
                day = hr["dayOfWeek"]
                openstr = hr["opens"] + " am - "
                closestr = hr["closes"]
                close = int(closestr.split(":", 1)[0])
                if close > 12:
                    close = close - 12
                hours = (
                    hours
                    + day
                    + " "
                    + openstr
                    + str(close)
                    + ":"
                    + closestr.split(":", 1)[1]
                    + " pm "
                )
            lat, longt = (
                driver.page_source.split("destination=", 1)[1]
                .split('"', 1)[0]
                .split(",", 1)
            )

            yield SgRecord(
                locator_domain="https://www.bluefcu.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=SgRecord.MISSING,
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
