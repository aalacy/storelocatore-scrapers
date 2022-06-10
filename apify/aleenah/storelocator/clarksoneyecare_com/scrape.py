import json
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
logger = SgLogSetup().get_logger("clarksoneyecare_com")


def write_output(data):
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


def fetch_data():
    url = "https://www.clarksoneyecare.com/locations"
    res = session.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    script = (
        str(soup.find("script", {"id": "__NEXT_DATA__"}))
        .replace('<script id="__NEXT_DATA__" type="application/json">', "")
        .replace("</script>", "")
    )
    loc_list = json.loads(script)["props"]["pageProps"]["locations"]
    for loc in loc_list:
        url = "https://www.clarksoneyecare.com/locations/" + loc["slug"]
        logger.info(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        schema = res.text.split('<script type="application/ld+json">')[2].split(
            "</script>", 1
        )[0]
        schema = schema.replace("\n", "")
        script = json.dumps(schema)
        script = json.loads(script)
        days = json.loads(script)["openingHoursSpecification"]
        tim = ""
        for day in days:
            tim += day["dayOfWeek"] + ": " + day["opens"] + " - " + day["closes"] + ", "

        tim = tim.strip(", ")
        street = loc["address1"].strip()
        if "address2" in loc:
            street += " " + loc["address2"].strip()
        if "address3" in loc:
            street += " " + loc["address3"].strip()
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
