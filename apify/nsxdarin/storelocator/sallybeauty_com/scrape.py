from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("sallybeauty_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=None,
)


def fetch_data():
    ids = []
    canadaurls = [
        "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Winnipeg%2C%20AB&radius=300",
        "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Vancouver%2C%20BC&radius=300",
        "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Montreal%2C%20QC&radius=300",
        "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=St.%20John%27s%2C%20NL&radius=300",
        "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Calgary%2C%20AB&radius=300",
        "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Toronto%2C%20ON&radius=300",
    ]
    for curl in canadaurls:
        url = curl
        logger.info(("Pulling Canada URL %s..." % curl))
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ""
                loc = "<MISSING>"
                add = ""
                city = ""
                state = ""
                zc = ""
                country = ""
                typ = "<MISSING>"
                lat = ""
                lng = ""
                phone = ""
                website = "sallybeauty.com"
                store = line.split('"ID": "')[1].split('"')[0]
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if '"address1": "' in line:
                add = line.split('"address1": "')[1].split('"')[0]
            if '"address2": "' in line:
                add = add + " " + line.split('"address2": "')[1].split('"')[0]
                add = add.strip()
            if '"city": "' in line:
                city = line.split('"city": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line:
                lat = line.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line:
                lng = line.split('"longitude": ')[1].split(",")[0]
            if '"phone": "' in line:
                phone = line.split('"phone": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                cas = [
                    "AB",
                    "BC",
                    "MB",
                    "NL",
                    "ON",
                    "NB",
                    "QC",
                    "PQ",
                    "SK",
                    "PE",
                    "PEI",
                ]
                if state in cas:
                    country = "CA"
                if store not in ids and country == "CA":
                    ids.append(store)
                    logger.info(("Pulling Store ID #%s..." % store))
                    hours = "<MISSING>"
                    if store == "store_10777":
                        zc = "06473"
                    if "." in lat and "." in lng:
                        loc = (
                            "https://www.sallybeauty.com/store-details/?showMap=true&horizontalView=true&lat="
                            + lat
                            + "&long="
                            + lng
                        )
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

    for xlat, ylng in search:
        x = xlat
        y = ylng
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        url = (
            "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=50&lat="
            + str(x)
            + "&long="
            + str(y)
        )
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ""
                loc = "<MISSING>"
                add = ""
                city = ""
                state = ""
                zc = ""
                country = ""
                typ = "<MISSING>"
                lat = ""
                lng = ""
                phone = ""
                website = "sallybeauty.com"
                store = line.split('"ID": "')[1].split('"')[0]
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if '"address1": "' in line:
                add = line.split('"address1": "')[1].split('"')[0]
            if '"address2": "' in line:
                add = add + " " + line.split('"address2": "')[1].split('"')[0]
                add = add.strip()
            if '"city": "' in line:
                city = line.split('"city": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line:
                lat = line.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line:
                lng = line.split('"longitude": ')[1].split(",")[0]
            if '"phone": "' in line:
                phone = line.split('"phone": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                if store not in ids and " " not in zc:
                    ids.append(store)
                    logger.info(("Pulling Store ID #%s..." % store))
                    hours = "<MISSING>"
                    country = "US"
                    if zc == "":
                        zc = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if store == "store_10777":
                        zc = "06473"
                    if "." in lat and "." in lng:
                        loc = (
                            "https://www.sallybeauty.com/store-details/?showMap=true&horizontalView=true&lat="
                            + lat
                            + "&long="
                            + lng
                        )
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
        x = float(float(xlat) - 0.25)
        y = float(float(ylng) - 0.25)
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        url = (
            "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=50&lat="
            + str(x)
            + "&long="
            + str(y)
        )
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ""
                loc = "<MISSING>"
                add = ""
                city = ""
                state = ""
                zc = ""
                country = ""
                typ = "<MISSING>"
                lat = ""
                lng = ""
                phone = ""
                website = "sallybeauty.com"
                store = line.split('"ID": "')[1].split('"')[0]
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if '"address1": "' in line:
                add = line.split('"address1": "')[1].split('"')[0]
            if '"address2": "' in line:
                add = add + " " + line.split('"address2": "')[1].split('"')[0]
                add = add.strip()
            if '"city": "' in line:
                city = line.split('"city": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line:
                lat = line.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line:
                lng = line.split('"longitude": ')[1].split(",")[0]
            if '"phone": "' in line:
                phone = line.split('"phone": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                if store not in ids and " " not in zc:
                    ids.append(store)
                    logger.info(("Pulling Store ID #%s..." % store))
                    hours = "<MISSING>"
                    country = "US"
                    if zc == "":
                        zc = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if store == "store_10777":
                        zc = "06473"
                    if "." in lat and "." in lng:
                        loc = (
                            "https://www.sallybeauty.com/store-details/?showMap=true&horizontalView=true&lat="
                            + lat
                            + "&long="
                            + lng
                        )
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
        x = float(float(xlat) + 0.25)
        y = float(float(ylng) + 0.25)
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        url = (
            "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=50&lat="
            + str(x)
            + "&long="
            + str(y)
        )
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ""
                loc = "<MISSING>"
                add = ""
                city = ""
                state = ""
                zc = ""
                country = ""
                typ = "<MISSING>"
                lat = ""
                lng = ""
                phone = ""
                website = "sallybeauty.com"
                store = line.split('"ID": "')[1].split('"')[0]
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if '"address1": "' in line:
                add = line.split('"address1": "')[1].split('"')[0]
            if '"address2": "' in line:
                add = add + " " + line.split('"address2": "')[1].split('"')[0]
                add = add.strip()
            if '"city": "' in line:
                city = line.split('"city": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line:
                lat = line.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line:
                lng = line.split('"longitude": ')[1].split(",")[0]
            if '"phone": "' in line:
                phone = line.split('"phone": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                if store not in ids and " " not in zc:
                    ids.append(store)
                    logger.info(("Pulling Store ID #%s..." % store))
                    hours = "<MISSING>"
                    country = "US"
                    if zc == "":
                        zc = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if store == "store_10777":
                        zc = "06473"
                    if "." in lat and "." in lng:
                        loc = (
                            "https://www.sallybeauty.com/store-details/?showMap=true&horizontalView=true&lat="
                            + lat
                            + "&long="
                            + lng
                        )
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
