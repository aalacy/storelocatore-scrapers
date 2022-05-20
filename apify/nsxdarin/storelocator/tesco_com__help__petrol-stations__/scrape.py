from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from tenacity import retry, stop_after_attempt
import tenacity

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tesco_com__help__petrol-stations__")


@retry(stop=stop_after_attempt(7), wait=tenacity.wait_fixed(7))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def fetch_data():
    locs = []
    url = "https://www.tesco.com/store-locator/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'hreflang="en" href="https://www.tesco.com/store-locator/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl.count("/") == 5:
                locs.append(lurl)
    for loc in locs:
        Petrol = False
        try:
            website = "tesco.com/help/petrol-stations/"
            typ = "Petrol Filling Station"
            country = "GB"
            state = "<MISSING>"
            hours = ""
            name = ""
            store = ""
            add = ""
            city = ""
            zc = ""
            phone = "<MISSING>"
            lat = ""
            lng = ""
            logger.info(loc)
            r = get_response(loc)
            for line in r.iter_lines():
                if 'itemprop="name">Petrol Filling Station</h3>' in line:
                    Petrol = True
                if (
                    '"main store Petrol Filling Station hours dropdown"' in line
                    and Petrol is True
                ):
                    days = (
                        line.split(
                            '"main store Petrol Filling Station hours dropdown"'
                        )[1]
                        .split("data-days='[")[1]
                        .split("]' data-utc")[0]
                        .split('"day":"')
                    )
                    for day in days:
                        if '"intervals"' in day:
                            if '"isClosed":false' not in day:
                                hrs = day.split('"')[0] + ": Closed"
                            else:
                                hrs = (
                                    day.split('"')[0]
                                    + ": "
                                    + day.split('"start":')[1].split("}")[0]
                                    + "-"
                                    + day.split('"end":')[1].split(",")[0]
                                )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    phone = (
                        line.split(
                            '"main store Petrol Filling Station hours dropdown"'
                        )[1]
                        .split('Phone-display">')[1]
                        .split("<")[0]
                    )
                if '"pageName":"' in line:
                    name = line.split('"pageName":"')[1].split('"')[0]
                    store = line.split('"storeID":"')[1].split('"')[0]
                if 'itemprop="latitude" content="' in line:
                    lat = line.split('itemprop="latitude" content="')[1].split('"')[0]
                    lng = line.split('itemprop="longitude" content="')[1].split('"')[0]
                if 'itemprop="postalCode">' in line:
                    zc = line.split('itemprop="postalCode">')[1].split("<")[0]
                if 'Address-city">' in line:
                    city = line.split('Address-city">')[1].split("<")[0]
                if 'itemprop="streetAddress" content="' in line:
                    add = line.split('itemprop="streetAddress" content="')[1].split(
                        '"'
                    )[0]
                if 'itemprop="openingHours" content="' in line and Petrol is False:
                    days = line.split('itemprop="openingHours" content="')
                    for day in days:
                        if '<div class="About-dropdown">' not in day:
                            hrs = day.split('"')[0]
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if "id=;" in hours:
                hours = hours.split("id=;")[1]
            if Petrol:
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
