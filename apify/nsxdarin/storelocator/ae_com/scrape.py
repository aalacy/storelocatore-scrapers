from xml.etree import ElementTree as ET
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("ae_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

website = "https://storelocations.ae.com"

MISSING = "<MISSING>"


def getXMLRoot(text):
    return ET.fromstring(text)


def getXMLObjectVariable(Object, varNames, noVal=MISSING, noText=False):
    Object = [Object]
    for varName in varNames.split("."):
        value = []
        for element in Object[0]:
            if varName == element.tag:
                value.append(element)
        if len(value) == 0:
            return noVal
        Object = value

    if noText is True:
        return Object
    if len(Object) == 0 or Object[0].text is None:
        return MISSING
    return Object[0].text


def request_with_retries(url):
    r = session.get(url, headers=headers)
    return r


def fetchStores():
    response = request_with_retries(f"{website}/sitemap.xml")
    data = getXMLRoot(
        response.text.replace('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', "")
    )
    links = []
    for url in getXMLObjectVariable(data, "url", [], True):
        links.append(getXMLObjectVariable(url, "loc"))
    return links


page_urls = fetchStores()


def fetch_data():
    page_urls.append(
        "https://storelocations.ae.com/us/ky/louisville/4801/c564-outer-loop.html"
    )
    locs = []
    for page in page_urls:
        if page.count("/") >= 6 and ".com/es/" not in page and ".com/fr/" not in page:
            locs.append(page)
    for loc in locs:
        try:
            logger.info("Pulling Location %s..." % loc)
            website = "ae.com"
            typ = ""
            hours = ""
            phone = ""
            name = ""
            add = ""
            lat = ""
            lng = ""
            city = ""
            store = ""
            state = ""
            zc = ""
            country = loc.split(".com/")[1].split("/")[0].upper()
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("<")[0].replace("&amp;", "&")
                if "days='[" in line2:
                    days = line2.split("days='[")[1].split("]}]'")[0].split('"day":"')
                    for day in days:
                        if '"intervals":' in day:
                            dname = day.split('"')[0]
                            try:
                                hrs = (
                                    day.split('"start":')[1].split("}")[0]
                                    + "-"
                                    + day.split('"end":')[1].split(",")[0]
                                )
                                if hours == "":
                                    hours = dname + ": " + hrs
                                else:
                                    hours = hours + "; " + dname + ": " + hrs
                            except:
                                hours = "CLOSED"
                if '<span class="c-address-street-1">' in line2:
                    add = line2.split('<span class="c-address-street-1">')[1].split(
                        "<"
                    )[0]
                    if '<span class="c-address-street-2">' in line2:
                        add = (
                            add
                            + " "
                            + line2.split('<span class="c-address-street-2">')[1].split(
                                "<"
                            )[0]
                        )
                    city = line2.split('<span class="c-address-city">')[1].split("<")[0]
                    try:
                        state = line2.split('itemprop="addressRegion">')[1].split("<")[
                            0
                        ]
                    except:
                        state = "<MISSING>"
                    try:
                        zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                    except:
                        zc = "<MISSING>"
                    try:
                        phone = line2.split('itemprop="telephone">')[1].split("<")[0]
                    except:
                        phone = "<MISSING>"
                    lat = line2.split('type="text/data">{"latitude":')[1].split(",")[0]
                    lng = line2.split(',"longitude":')[1].split("}")[0]
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            store = "<MISSING>"
            if "American Eagle" in name and "Aerie Outlet" in name:
                name = "American Eagle & Aerie Outlet"
            if "American Eagle" in name and "Aerie Store" in name:
                name = "American Eagle & Aerie"
            if "Aerie Outlet" in name and "American Eagle" not in name:
                name = "Aerie Outlet"
            if "Aerie Store" in name and "American Eagle" not in name:
                name = "Aerie"
            if "American Eagle Outlet" in name and "Aerie" not in name:
                name = "American Eagle Outlet"
            if "OFFLINE" in name:
                name = "OFFLINE"
            if "American Eagle Store" in name and "Aerie" not in name:
                name = "American Eagle"
            if "American Eagle Outfitters" in name and "Aerie" not in name:
                name = "American Eagle"
            if "Unsubscribed" in name:
                name = "Unsubscribed"
            add = add.replace("&amp;", "&")
            hours = hours.replace("{:", "").strip()
            if city == "Winnipeg":
                add = add.replace("Suite CRU-101", "").strip()
            if country != "CA" and country != "US":
                state = "<MISSING>"
            name = name.replace("&#39;", "'")
            add = add.replace("&#39;", "'")
            city = city.replace("&#39;", "'")
            if city != "":
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
