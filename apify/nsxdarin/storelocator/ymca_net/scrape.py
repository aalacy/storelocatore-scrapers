from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=10,
)

logger = SgLogSetup().get_logger("ymca_org")


def fetch_data():
    alllocs = []
    for lat, lng in search:
        try:
            x = lat
            y = lng
            coords = []
            infos = []
            url = (
                "https://www.ymca.org/find-your-y?distance=250&lat="
                + str(x)
                + "&lng="
                + str(y)
                + "&geolocation_geocoder_address=&type=branch"
            )
            r = session.get(url, headers=headers)
            website = "ymca.org"
            typ = "<MISSING>"
            country = "US"
            logger.info(str(x) + "," + str(y))
            for line in r.iter_lines():
                line = str(line.decode("utf-8"))
                if (
                    'view-mode-location-listing node--promoted" data-entity-id="'
                    in line
                ):
                    store = line.split(
                        'view-mode-location-listing node--promoted" data-entity-id="'
                    )[1].split('"')[0]
                if 'data-marker-zoom-anchor-id="marker-' in line:
                    sid = line.split('data-marker-zoom-anchor-id="marker-')[1].split(
                        '"'
                    )[0]
                    llat = line.split('data-lat="')[1].split('"')[0]
                    llng = line.split('data-lng="')[1].split('"')[0]
                    coords.append(sid + "|" + llat + "|" + llng)
                if '<h4><a class="node__title-link" href="' in line:
                    loc = "https://www.ymca.org" + line.split('href="')[1].split('"')[0]
                    name = line.split('label-hidden">')[1].split("<")[0]
                    lat = ""
                    lng = ""
                    city = ""
                    state = ""
                    add = ""
                    zc = ""
                    hours = ""
                    if loc not in alllocs:
                        alllocs.append(loc)
                        r2 = session.get(loc, headers=headers)
                        HFound = False
                        logger.info(loc)
                        for line2 in r2.iter_lines():
                            line2 = str(line2.decode("utf-8"))
                            if "Hours of Operation</h4>" in line2:
                                HFound = True
                            if HFound and "</tbody>" in line2:
                                HFound = False
                            if HFound and "<td>" in line2:
                                hrs = line2.split("<td>")[1].split("<")[0]
                                if (
                                    "am" not in hrs
                                    and "pm" not in hrs
                                    and "Closed" not in hrs
                                ):
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                                else:
                                    hours = hours + " " + hrs
                if '<span class="address-line1">' in line:
                    add = line.split('<span class="address-line1">')[1].split("<")[0]
                if '<span class="address-line2">' in line:
                    add = (
                        add
                        + " "
                        + line.split('<span class="address-line2">')[1].split("<")[0]
                    )
                if '<span class="locality">' in line:
                    city = line.split('<span class="locality">')[1].split("<")[0]
                    state = line.split('="administrative-area">')[1].split("<")[0]
                    zc = line.split('class="postal-code">')[1].split("<")[0]
                if 'field__item"><a href="tel:+1-' in line:
                    phone = line.split('field__item"><a href="tel:+1-')[1].split('"')[0]
                    infos.append(
                        store
                        + "|"
                        + loc
                        + "|"
                        + name
                        + "|"
                        + add
                        + "|"
                        + city
                        + "|"
                        + state
                        + "|"
                        + zc
                        + "|"
                        + phone
                        + "|"
                        + hours
                    )
                if "</html>" in line:
                    for info in infos:
                        store = info.split("|")[0]
                        loc = info.split("|")[1]
                        name = info.split("|")[2]
                        add = info.split("|")[3]
                        city = info.split("|")[4]
                        state = info.split("|")[5]
                        zc = info.split("|")[6]
                        phone = info.split("|")[7]
                        hours = info.split("|")[8]
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                        for coord in coords:
                            if store == coord.split("|")[0]:
                                lat = coord.split("|")[1]
                                lng = coord.split("|")[2]
                        if phone == "":
                            phone = "<MISSING>"
                        if hours == "":
                            hours = "<MISSING>"
                        name = name.replace("&amp;", "&")
                        add = add.replace("&amp;", "&")
                        city = city.replace("&amp;", "&")
                        hours = hours.replace("&amp;", "&")
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
