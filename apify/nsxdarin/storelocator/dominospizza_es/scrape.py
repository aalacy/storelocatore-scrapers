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

logger = SgLogSetup().get_logger("dominospizza_es")


def fetch_data():
    url = "https://www.dominospizza.es/tiendas-dominos-pizza"
    r = session.get(url, headers=headers)
    locs = []
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="nm" href="/tiendas-dominos-pizza/tiendas/' in line:
            locs.append(
                "https://www.dominospizza.es/" + line.split('href="')[1].split('"')[0]
            )
    website = "dominospizza.es"
    typ = "<MISSING>"
    country = "ES"
    for loc in locs:
        logger.info(loc)
        zc = ""
        name = ""
        add = ""
        city = ""
        state = ""
        phone = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'itemprop="name" style="display: none">' in line2:
                name = (
                    line2.split('itemprop="name" style="display: none">')[1]
                    .split("<")[0]
                    .strip()
                )
            if 'itemprop="openingHours" content="' in line2:
                hours = line2.split('itemprop="openingHours" content="')[1].split('"')[
                    0
                ]
            if 'itemprop="streetAddress">' in line2:
                raw_address = line2.split('itemprop="streetAddress">')[1].split("<")[0]
                formatted_addr = parse_address_intl(raw_address)
                add = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    add = add + ", " + formatted_addr.street_address_2
                city = formatted_addr.city
                state = formatted_addr.state if formatted_addr.state else "<MISSING>"
                zc = formatted_addr.postcode if formatted_addr.postcode else "<MISSING>"
            if 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split("<")[0].strip()
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
            raw_address=raw_address,
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
