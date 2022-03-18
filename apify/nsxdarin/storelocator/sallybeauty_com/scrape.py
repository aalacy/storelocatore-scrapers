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
    max_search_distance_miles=None,
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
        try:
            for line in r.iter_lines():
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
                if '"storeHours": "' in line:
                    days = (
                        line.split('"storeHours": "')[1]
                        .split('</div>\\n",')[0]
                        .split("<div class='store-hours-day'>")
                    )
                    for day in days:
                        if '<span class=\\"hours-of-day\\">' in day:
                            hrs = (
                                day.split("\\n")[0]
                                + day.split('<span class=\\"hours-of-day\\">')[1].split(
                                    "<"
                                )[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
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
                        cstore = store.replace("store_", "")
                        logger.info(("Pulling Store ID #%s..." % store))
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
                            store_number=cstore,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )
        except:
            pass

    coordslist = [
        "32.159599,-110.989014",
        "18.143903,-65.808248",
        "17.979477,-66.095159",
        "18.231512,-65.904906",
        "18.123636,-66.133426",
        "18.237111,-66.03966",
        "18.241633,-66.03465",
        "18.247714,-66.025041",
        "18.235215,-66.058015",
        "18.340187,-66.068171",
        "18.375374,-65.927479",
        "18.379538,-65.886931",
        "18.3751,-65.831909",
        "18.3699,-66.015736",
        "18.392945,-65.97628",
        "18.370038,-66.06752",
        "18.394086,-65.998169",
        "18.344387,-65.674297",
        "18.3959,-66.042",
        "18.369607,-66.109966",
        "18.400184,-66.074873",
        "18.383624,-66.13986",
        "18.273583,-66.272398",
        "18.360518,-66.188032",
        "18.008161,-66.383825",
        "18.40543,-66.1603",
        "18.422852,-66.162718",
        "18.411,-66.3205",
        "18.464049,-66.272534",
        "18.043514,-66.577051",
        "18.431551,-66.473689",
        "17.995108,-66.638353",
        "18.025773,-66.855708",
        "18.481498,-66.769889",
        "18.09064,-67.030716",
        "18.343308,-66.993613",
        "18.468512,-67.02345",
        "18.243415,-67.1619",
        "18.425295,-67.149301",
        "40.074863,-80.876674",
        "40.439648,-80.001022",
        "40.487874,-79.888025",
        "40.454142,-80.163224",
        "40.584376,-79.708917",
        "40.525709,-80.007169",
        "40.367084,-80.671435",
        "40.646048,-79.71222",
        "40.683031,-80.105587",
        "40.682719,-80.305781",
        "40.876961,-79.948567",
        "41.191946,-79.394133",
        "41.126253,-78.733591",
        "61.576507,-149.403765",
        "61.226256,-149.743034",
        "61.140596,-149.86516",
        "64.851518,-147.704495",
        "44.02681,-116.942528",
        "43.610412,-116.591688",
        "43.550415,-116.571426",
        "43.635222,-116.357332",
        "43.617759,-116.285004",
        "43.577823,-116.194927",
        "18.360518,-66.188032",
        "18.369607,-66.109966",
        "18.40543,-66.1603",
        "18.422852,-66.162718",
        "18.340187,-66.068171",
        "18.370038,-66.06752",
        "18.400184,-66.074873",
        "18.273583,-66.272398",
        "18.3959,-66.042",
        "18.3699,-66.015736",
        "18.235215,-66.058015",
        "18.464049,-66.272534",
        "18.411,-66.3205",
        "18.237111,-66.03966",
        "18.241633,-66.03465",
        "18.247714,-66.025041",
        "18.394086,-65.998169",
        "18.392945,-65.97628",
        "18.123636,-66.133426",
        "18.375374,-65.927479",
        "18.379538,-65.886931",
        "18.231512,-65.904906",
        "18.431551,-66.473689",
        "18.3751,-65.831909",
        "17.979477,-66.095159",
        "18.143903,-65.808248",
        "18.008161,-66.383825",
        "18.344387,-65.674297",
        "18.043514,-66.577051",
        "17.995108,-66.638353",
        "18.481498,-66.769889",
        "18.025773,-66.855708",
        "18.343308,-66.993613",
        "18.468512,-67.02345",
        "18.09064,-67.030716",
        "18.425295,-67.149301",
        "18.243415,-67.1619",
        "43.5432355,-96.6576023",
        "25.589748,-80.357543",
        "25.645218,-80.335193",
        "25.653311,-80.414996",
        "25.682965,-80.313672",
        "25.697731,-80.383207",
        "25.732811,-80.3354",
        "25.73342,-80.376378",
        "25.713369,-80.450679",
        "25.761016,-80.304901",
        "25.770092,-80.34675",
        "25.478844,-80.462777",
        "25.791116,-80.367946",
        "25.772113,-80.255752",
        "25.766476,-80.198344",
        "25.809483,-80.195246",
        "25.848008,-80.293192",
        "25.788237,-80.140858",
        "25.867857,-80.293988",
        "25.89579,-80.350098",
        "25.891184,-80.16338",
        "25.937926,-80.297897",
        "25.927144,-80.172424",
        "25.980391,-80.374362",
        "25.933521,-80.122858",
        "26.006298,-80.308654",
        "26.012811,-80.250799",
        "25.985902,-80.155055",
        "26.010221,-80.186828",
        "26.064675,-80.36417",
        "26.042652,-80.159972",
        "26.094123,-80.247571",
        "26.092805,-80.156492",
        "26.144447,-80.316397",
        "26.149357,-80.269122",
        "26.146742,-80.120926",
        "26.196247,-80.254655",
        "26.190069,-80.123768",
        "26.246052,-80.252265",
        "26.270892,-80.204405",
        "26.285746,-80.248204",
        "26.262195,-80.098489",
        "26.316178,-80.156526",
        "26.315076,-80.090204",
        "26.354432,-80.204623",
        "26.367449,-80.07655",
        "26.460134,-80.126986",
        "26.5257,-80.0907",
        "26.59208,-80.14536",
        "26.66145,-80.265859",
        "26.638078,-80.087437",
        "26.685982,-80.202659",
        "26.720173,-80.112002",
        "26.10651,-81.750333",
        "26.208448,-81.766958",
        "26.269272,-81.799256",
        "26.331897,-81.809359",
        "26.40443,-81.810192",
        "26.48398,-81.789363",
        "26.511792,-81.944755",
    ]

    for latlng in coordslist:
        x = latlng.split(",")[0]
        y = latlng.split(",")[1]
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        url = (
            "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=250&radius=250&lat="
            + str(x)
            + "&long="
            + str(y)
        )
        r = session.get(url, headers=headers)
        try:
            for line in r.iter_lines():
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
                if '"storeHours": "' in line:
                    days = (
                        line.split('"storeHours": "')[1]
                        .split('</div>\\n",')[0]
                        .split("<div class='store-hours-day'>")
                    )
                    for day in days:
                        if '<span class=\\"hours-of-day\\">' in day:
                            hrs = (
                                day.split("\\n")[0]
                                + day.split('<span class=\\"hours-of-day\\">')[1].split(
                                    "<"
                                )[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    if store not in ids and " " not in zc:
                        cstore = store.replace("store_", "")
                        ids.append(store)
                        logger.info(("Pulling Store ID #%s..." % store))
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
                            store_number=cstore,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )
        except:
            pass

    for xlat, ylng in search:
        x = xlat
        y = ylng
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        url = (
            "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=250&radius=250&lat="
            + str(x)
            + "&long="
            + str(y)
        )
        r = session.get(url, headers=headers)
        try:
            for line in r.iter_lines():
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
                if '"storeHours": "' in line:
                    days = (
                        line.split('"storeHours": "')[1]
                        .split('</div>\\n",')[0]
                        .split("<div class='store-hours-day'>")
                    )
                    for day in days:
                        if '<span class=\\"hours-of-day\\">' in day:
                            hrs = (
                                day.split("\\n")[0]
                                + day.split('<span class=\\"hours-of-day\\">')[1].split(
                                    "<"
                                )[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    if store not in ids and " " not in zc:
                        cstore = store.replace("store_", "")
                        ids.append(store)
                        logger.info(("Pulling Store ID #%s..." % store))
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
                            store_number=cstore,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
