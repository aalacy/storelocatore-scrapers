from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("costco_com__gasoline.html")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


@retry(stop=stop_after_attempt(10))
def fetch_loc(loc):
    session = SgRequests()
    return session.get(loc, headers=headers)


def fetch_data():
    locs = []
    url = "https://www.costco.com/sitemap_l_001.xml"
    r = fetch_loc(url)
    for raw_line in r.iter_lines():
        line = str(raw_line)
        if "<loc>https://www.costco.com/warehouse-locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        website = "costco.com/gasoline.html"
        name = "<MISSING>"
        typ = "Warehouse"
        hours = ""
        phone = ""
        add = ""
        city = ""
        zc = ""
        state = ""
        lat = ""
        lng = ""
        store = ""
        country = "US"
        IsGas = False
        HFound = False
        r2 = fetch_loc(loc)
        for raw_line2 in r2.iter_lines():
            line2 = str(raw_line2)
            if "Gas Hours</span>" in line2:
                IsGas = True
                HFound = True
            if HFound and 'gas-price-section">' in line2:
                HFound = False
            if HFound and 'itemprop="openingHours" datetime="' in line2:
                hrs = (
                    line2.split('itemprop="openingHours" datetime="')[1]
                    .split('"')[0]
                    .strip()
                )
                if hours == "":
                    hours = hrs
                else:
                    if "pm" in hrs:
                        hours = hours + ": " + hrs
                    else:
                        hours = hours + "; " + hrs
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'data-identifier="' in line2:
                store = line2.split('data-identifier="')[1].split('"')[0]
            if "<h1" in line2:
                name = (
                    line2.split("<h1")[1]
                    .split(">")[1]
                    .split("<")[0]
                    .replace("&nbsp;", " ")
                )
            if '"streetAddressOutput">' in line2:
                add = line2.split('"streetAddressOutput">')[1].split("<")[0]
            if 'addressLocalityOutput">' in line2:
                city = line2.split('addressLocalityOutput">')[1].split("<")[0]
            if '"addressRegionOutput">' in line2:
                state = line2.split('"addressRegionOutput">')[1].split("<")[0]
            if 'zipCodeOutput">' in line2:
                zc = line2.split('zipCodeOutput">')[1].split("<")[0]
            if phone == "" and 'telephoneOutput">' in line2:
                phone = (
                    line2.split('telephoneOutput">')[1]
                    .split("<")[0]
                    .strip()
                    .replace("\t", "")
                )
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if add != "" and IsGas is True:
            loc = loc.replace("/ ", "/").replace(" ", "-")
            if "colchester-vt-314" in loc:
                hours = "Mon-Fri.: 6:00am - 1:30pm, 6:00pm - 9:00pm; Sat.: 7:00am - 9:30am, 6:00pm - 8:00pm; Sun.: 7:00am - 7:00pm"
            if "w-san-antonio-san-antonio-tx-1449" in loc:
                hours = "Mon-Fri.: 6:00am - 9:00pm; Sat.: 7:00am - 7:00pm; Sun.: 7:00am - 7:00pm"
            if "las-vegas-bus-ctr-las-vegas-nv-563" in loc:
                hours = "Mon-Fri.: 6:00am - 7:00pm; Sat.: 6:00am - 5:00pm; Sun.: 9:00am - 6:00pm"
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
