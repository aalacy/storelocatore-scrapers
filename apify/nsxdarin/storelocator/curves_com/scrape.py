from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("curves_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    ids = []
    for clat, clng in search:
        logger.info(str(clat) + "-" + str(clng))
        url = (
            "https://www.curves.com/find-a-club?location=10002&lat="
            + str(clat)
            + "&lng="
            + str(clng)
        )
        try:
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if ">&#x1F4DE;</i>" in line:
                    phone = line.split(">&#x1F4DE;</i>")[1].split("<")[0]
                if '<a href="https://www.wellnessliving.com' in line:
                    purl = line.split('href="')[1].split('"')[0]
                    if purl not in ids:
                        ids.append(purl)
                        r2 = session.get(purl, headers=headers)
                        name = ""
                        website = "curves.com"
                        typ = "Fitness Studio"
                        add = ""
                        city = ""
                        state = ""
                        zc = ""
                        country = "US"
                        store = "<MISSING>"
                        lat = ""
                        lng = ""
                        hours = ""
                        for line2 in r2.iter_lines():
                            if '<meta name="geo.position" content="' in line2:
                                lat = line2.split(
                                    '<meta name="geo.position" content="'
                                )[1].split(";")[0]
                                lng = (
                                    line2.split('<meta name="geo.position" content="')[
                                        1
                                    ]
                                    .split(";")[1]
                                    .split('"')[0]
                                )
                            if '"geo.placename" content="' in line2:
                                name = line2.split('"geo.placename" content="')[
                                    1
                                ].split('"')[0]
                            if 'margin:0;">  <li> <img alt="' in line2:
                                typ = line2.split('margin:0;">  <li> <img alt="')[
                                    1
                                ].split(" in ")[0]
                            if '<span itemprop="streetAddress">' in line2:
                                add = line2.split('<span itemprop="streetAddress">')[
                                    1
                                ].split("<")[0]
                                city = line2.split('itemprop="addressLocality">')[
                                    1
                                ].split("<")[0]
                                state = line2.split('<span itemprop="addressRegion">')[
                                    1
                                ].split("<")[0]
                                zc = line2.split('itemprop="postalCode">')[1].split(
                                    "<"
                                )[0]
                            if 'class="rs-microsite-right-day-column"><span>' in line2:
                                alldays = []
                                allhrs = []
                                days = (
                                    line2.split('right-day-column">')[1]
                                    .split("<br /></div>")[0]
                                    .split("<br />")
                                )
                                for day in days:
                                    if "</span>" in day:
                                        dname = day.rsplit(">")[1].split("<")[0]
                                        alldays.append(dname)
                                hrs = (
                                    line2.split('right-time-column">')[1]
                                    .split("<br /></div>")[0]
                                    .split("<br />")
                                )
                                for hour in hrs:
                                    if "</span>" in hour:
                                        if hour.count("</span>") == 1:
                                            allhrs.append(
                                                hour.split(">")[1].split("<")[0]
                                            )
                                        else:
                                            allhrs.append(hour.split("</span>")[1])
                                for x in range(0, len(alldays)):
                                    if hours == "":
                                        hours = alldays[x] + ": " + allhrs[x]
                                    else:
                                        hours = (
                                            hours + "; " + alldays[x] + ": " + allhrs[x]
                                        )
                        if hours == "":
                            hours = "<MISSING>"
                        if phone == "":
                            phone = "<MISSING>"
                        if add != "":
                            yield SgRecord(
                                locator_domain=website,
                                page_url=purl,
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
