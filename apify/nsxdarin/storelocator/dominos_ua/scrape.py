from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_ua")


def fetch_data():
    url = "https://dominos.ua/uk/odessa/where_to_buy/"
    r = session.get(url, headers=headers)
    website = "dominos.ua"
    typ = "<MISSING>"
    country = "UA"
    loc = "<MISSING>"
    zc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "window.app_props" in line:
            items = line.split("u0022location_code")
            for item in items:
                if "window.app_props" not in item:
                    hours = ""
                    store = item.split("\\u0022: \\u0022")[1].split("\\")[0]
                    name = item.split("name\\u0022: \\u0022")[1].split("\\u00")[0]
                    add = item.split("address\\u0022: \\u0022")[1].split("\\u00")[0]
                    lat = item.split("lat\\u0022: ")[1].split(",")[0]
                    lng = item.split("lng\\u0022: ")[1].split("}")[0]
                    days = (
                        item.split("u0022hours")[1]
                        .split("}],")[0]
                        .split("u0022name\\u0022: \\u0022")
                    )
                    for day in days:
                        if "text\\u0022" in day:
                            hrs = (
                                day.split("\\")[0]
                                + ": "
                                + day.split("text\\u0022: \\u0022")[1]
                                .split("\\u0022")[0]
                                .replace("\\u002D", "-")
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    city = item.split("city_name\\u0022: \\u0022")[1].split("\\")[0]
                    state = "<MISSING>"
                    phone = "<MISSING>"
                    yield SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        phone=phone,
                        location_type=typ,
                        store_number=store,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                    )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
