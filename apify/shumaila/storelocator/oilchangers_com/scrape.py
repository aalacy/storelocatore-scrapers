from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "oilchangers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://oilchangers.com"
MISSING = SgRecord.MISSING


def fetch_data():

    url = "https://oilchangers.com/wp-admin/admin-ajax.php"
    loclist = session.post(
        url, headers=headers, data={"action": "get_all_stores"}
    ).json()
    for loc in loclist:
        loc = loclist[loc]
        location_type = MISSING
        store = loc["ID"]
        title = loc["na"]
        link = loc["gu"]
        if "coming-soon" in link:
            location_type = "Coming Soon"
        log.info(link)
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["st"]
        city = str(loc["ct"])
        state = loc["rg"]
        pcode = loc["zp"]
        try:
            phone = loc["te"]
        except:
            phone = MISSING
        if len(city) < 3 and "5710 " in street:
            city = "El Paso"
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.find("div", {"class": "store_locator_single_opening_hours"})
            .text.replace("Opening Hours", "")
            .strip()
        )
        hours = hours.encode("ascii", "ignore").decode("ascii")
        phone = phone.encode("ascii", "ignore").decode("ascii")
        street = street.encode("ascii", "ignore").decode("ascii")
        city = city.encode("ascii", "ignore").decode("ascii")
        state = state.encode("ascii", "ignore").decode("ascii")
        pcode = pcode.encode("ascii", "ignore").decode("ascii")
        title = title.encode("ascii", "ignore").decode("ascii")

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=location_type,
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
