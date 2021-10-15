import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("clarksoneyecare_com")


def write_output(data):
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here

    url = "https://www.clarksoneyecare.com/_next/data/oZIpffJn05XGI8Sg6t6gs/locations.json"

    res = session.get(url)
    loc_list = res.json()["pageProps"]["locations"]
    logger.info(len(loc_list))

    for loc in loc_list:

        url = "https://www.clarksoneyecare.com/locations/" + loc["slug"]
        logger.info(url)
        logger.info(loc)

        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        script = (
            str(soup.find("script", {"type": "application/ld+json"}))
            .replace('<script type="application/ld+json">', "")
            .replace("</script>", "")
        )
        days = json.loads(script)["openingHoursSpecification"]
        tim = ""
        for day in days:
            tim += day["dayOfWeek"] + ": " + day["opens"] + " - " + day["closes"] + ", "

        tim = tim.strip(", ")

        if "address2" in loc and "address3" in loc:
            street = (
                loc["address1"] + " " + loc["address2"] + " " + loc["address3"].strip()
            )
        elif "address3" not in loc and "address2" in loc:
            street = loc["address1"] + " " + loc["address2"].strip()
        elif "address2" in loc and "address3" in loc:
            street = loc["address1"].strip()

        yield SgRecord(
            locator_domain="https://www.clarksoneyecare.com",
            page_url=url,
            location_name=loc["name"],
            street_address=street,
            city=loc["city"],
            state=loc["state"],
            zip_postal=loc["zipCode"],
            country_code="US",
            store_number="<MISSING>",
            phone=loc["phoneNumber"],
            location_type="<MISSING>",
            latitude=loc["map"]["lat"],
            longitude=loc["map"]["lon"],
            hours_of_operation=tim,
        )


def scrape():
    write_output(fetch_data())


scrape()
