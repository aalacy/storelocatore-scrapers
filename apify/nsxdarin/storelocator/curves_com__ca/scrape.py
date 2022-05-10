from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("curves_com__ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "cookie": "_omappvp=Pf5A9mseSdMvgpLpn7xhT03WNvE6GBVeTee8xRClU09hVWFyuHm11TuncHAN0lymqxFrsrRPCDBAC0pWRtiXHM8vnLXVxIoo; _gcl_au=1.1.702983292.1635276560; _ga=GA1.2.1556144746.1635276560; _gid=GA1.2.61177968.1635276560; _gat_UA-23879052-1=1; _fbp=fb.1.1635276560465.1159219933; wp-wpml_current_language=en; _agree_to_privacy_policy=true; _omappvs=1635276598770; _uetsid=045bbf30369311ec85c4719591a2b53e; _uetvid=8a2c6f10c31911eb9581e151293c3bab",
}


def fetch_data():
    ids = []
    canada = [
        "ON",
        "SK",
        "YT",
        "PEI",
        "PE",
        "NB",
        "NL",
        "NS",
        "AB",
        "MB",
        "BC",
        "QC",
        "NV",
        "NU",
        "NT",
    ]
    website = "curves.com"
    typ = "Fitness Studio"
    country = "CA"
    purl = "<MISSING>"
    name = "Curves (Kanata, ON)"
    add = "462 Hazeldean Rd., Unit #17"
    city = "Kanata"
    state = "ON"
    zc = "K2L 1V3"
    store = "<MISSING>"
    phone = "613-254-5704"
    hours = "<MISSING>"
    lat = "45.2983929"
    lng = "-75.8883216"
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
    for xlat in range(43, 70):
        for ylng in range(-80, -52):
            url = (
                "https://www.curves.com/ca/find-a-club?location=Toronto,%20ON&lat="
                + str(xlat)
                + "&lng="
                + str(ylng)
            )
            logger.info(url)
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if ">&#x1F4DE;</i>" in line:
                    phone = line.split("tel:")[1].split('"')[0]
                if '<a href="https://www.wellnessliving.com' in line:
                    purl = line.split('href="')[1].split('"')[0]
                    logger.info(purl)
                    if purl not in ids:
                        ids.append(purl)
                        r2 = session.get(purl, headers=headers)
                        logger.info("Pulling Location %s..." % purl)
                        name = ""
                        website = "curves.com"
                        typ = "Fitness Studio"
                        add = ""
                        city = ""
                        state = ""
                        zc = ""
                        country = "CA"
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
                        if add != "" and state in canada:
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


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
