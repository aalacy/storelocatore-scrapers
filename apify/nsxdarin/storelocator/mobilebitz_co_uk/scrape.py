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
    url = ""
    r = session.get(url, headers=headers)
    website = "https://mobilebitz.co.uk/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1643389582324"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<item><location>" in line:
            name = line.split("<item><location>")[1].split("<")[0]
            rawadd = (
                line.split("<address>")[1]
                .split("<")[0]
                .replace("&amp;#44;", ",")
                .replace("&amp;#39;", "'")
                .replace("  ", " ")
                .replace("&#44;", ",")
                .replace("&#39;", "'")
                .replace(" ,", ",")
                .replae(", ", ",")
            )
            formatted_addr = parse_address_intl(rawadd)
            add = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                add = add + ", " + formatted_addr.street_address_2
            city = formatted_addr.city
            state = formatted_addr.state if formatted_addr.state else "<MISSING>"
            zc = formatted_addr.postcode if formatted_addr.postcode else "<MISSING>"
            store = line.split("<storeId>")[1].split("<")[0]
            lat = line.split("<latitude>")[1].split("<")[0]
            lng = line.split("<longitude>")[1].split("<")[0]
            phone = line.split("<telephone>")[1].split("<")[0]
            hours = ""
            days = (
                line.split("<operatingHours")[1]
                .split("</operatingHours>")[0]
                .split('text-align: left;">')
            )
            for day in days:
                if 'text-align: right;">' in day:
                    hrs = (
                        day.split("<")[0]
                        + ": "
                        + day.split('text-align: right;">')[1].split("<")[0]
                    )
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            loc = "<MISSING>"
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
