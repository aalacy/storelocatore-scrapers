from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("mobilebitz_co_uk")


def fetch_data():
    url = "https://mobilebitz.co.uk/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1643389582324"
    r = session.get(url, headers=headers)
    website = "mobilebitz.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "https://mobilebitz.co.uk/store-list/"
    name = "MobileBitz Kiosk, Westfield"
    add = "Westfield Shopping Centre, Shepherd's Bush"
    city = "London"
    state = "<MISSING>"
    zc = "W12 7GF"
    phone = "02039529027"
    rawadd = (
        "Westfield Shopping Centre, Shepherd's Bush, Shepherd's Bush London, W12 7GF"
    )
    lat = "51.5075725"
    lng = "-0.2212054"
    store = "2"
    hours = "Mon: 10:00 - 21:00; Tue: 10:00 - 21:00; Wed: 10:00 - 21:00; Thu: 10:00 - 21:00; Fri: 10:00 - 21:00; Sat: 10:00 - 21:00; Sun: 12:00-18:00"
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
        raw_address=rawadd,
        hours_of_operation=hours,
    )
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<item><location>" in line:
            items = line.split("<item><location>")
            for item in items:
                if "<storeId>" in item:
                    name = item.split("<")[0]
                    rawadd = (
                        item.split("<address>")[1]
                        .split("<")[0]
                        .replace("&amp;#44;", ",")
                        .replace("&amp;#39;", "'")
                        .replace("  ", " ")
                        .replace("&#44;", ",")
                        .replace("&#39;", "'")
                        .replace(" ,", ",")
                        .replace(", ", ",")
                    )
                    formatted_addr = parse_address_intl(rawadd)
                    add = ""
                    city = ""
                    state = ""
                    zc = ""
                    add = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        add = add + ", " + formatted_addr.street_address_2
                    city = formatted_addr.city
                    state = (
                        formatted_addr.state if formatted_addr.state else "<MISSING>"
                    )
                    zc = (
                        formatted_addr.postcode
                        if formatted_addr.postcode
                        else "<MISSING>"
                    )
                    store = item.split("<storeId>")[1].split("<")[0]
                    lat = item.split("<latitude>")[1].split("<")[0]
                    lng = item.split("<longitude>")[1].split("<")[0]
                    phone = item.split("<telephone>")[1].split("<")[0]
                    hours = ""
                    days = (
                        item.split("<operatingHours")[1]
                        .split("</operatingHours>")[0]
                        .split("text-align: left;&quot;&gt;")
                    )
                    for day in days:
                        if "text-align: right;&quot;&gt;" in day:
                            hrs = (
                                day.split("&lt;")[0]
                                + ": "
                                + day.split("text-align: right;&quot;&gt;")[1].split(
                                    "&lt;"
                                )[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    loc = "https://mobilebitz.co.uk/store-list/"
                    if "Bluewater" in name:
                        city = "Bluewater"
                    if "BD1 1US" in rawadd:
                        zc = "BD1 1US"
                    if "SW19 8YA" in rawadd:
                        zc = "SW19 8YA"
                    if "Meadowhall" in name:
                        zc = "S9 1EN"
                        city = "Meadowhall"
                        add = "91a High Street"
                    add = (
                        add.replace("&amp;#44;", ",")
                        .replace("&amp;", "&")
                        .replace("&amp", "&")
                        .replace("&Amp", "&")
                    )
                    rawadd = (
                        rawadd.replace("&amp;#44;", ",")
                        .replace("&amp;", "&")
                        .replace("&amp", "&")
                        .replace("&Amp", "&")
                    )
                    name = (
                        name.replace("&amp;#44;", ",")
                        .replace("&amp;", "&")
                        .replace("&amp", "&")
                        .replace("&Amp", "&")
                    )
                    if phone != "02039529027":
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
                            raw_address=rawadd,
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
