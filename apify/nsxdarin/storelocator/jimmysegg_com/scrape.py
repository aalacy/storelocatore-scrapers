from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from tenacity import retry, stop_after_attempt
import tenacity

logger = SgLogSetup().get_logger("jimmysegg_com")

headers_ = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "referer": "https://www.jimmysegg.com/online-ordering/",
    "agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url, headers_c):
    with SgRequests(timeout_config=300) as http:
        logger.info(f"Pulling the data from: {url}")
        r = http.get(url, headers=headers_c)
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(
            f"Please fix GetResponseRetryError >> TemporaryError HttpStatusCode: {r.status_code}"
        )


def fetch_data():
    locs = []
    url = "https://www.jimmysegg.com/online-ordering/"
    r = get_response(url, headers_)
    website = "jimmysegg.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "ORDER NOW<" in line:
            locs.append(line.split('href="')[1].split('"')[0])
    logger.info(f"Total Store Count: {len(locs)}")
    for idx2, loc in enumerate(locs[0:]):
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        HFound = False
        hours = ""
        logger.info(f"[{idx2}] Pulling the data for {loc} ")
        r2 = get_response(loc, headers_)
        lines = r2.iter_lines()
        for line2 in lines:
            if "Hours of Business</div>" in line2:
                HFound = True
            if HFound and "carryout" in line2:
                HFound = False
            if HFound and '<div class="hours-day">' in line2:
                g = next(lines)
                day = g.split("<")[0].strip().replace("\t", "")
            if HFound and '<div class="hours-time">' in line2:
                g = next(lines)
                day = (
                    day
                    + ": "
                    + g.replace("\r", "").replace("\t", "").replace("\n", "").strip()
                )
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0].replace("\\u0027", "'")
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '<h1 class="restaurant-name">' in line2:
                name = (
                    line2.split('<h1 class="restaurant-name">')[1]
                    .split("<")[0]
                    .strip()
                    .replace("&#39;", "'")
                )
            if "var _locationLat = " in line2:
                lat = line2.split("var _locationLat = ")[1].split(";")[0]
            if "var _locationLng = " in line2:
                lng = line2.split("var _locationLng = ")[1].split(";")[0]
            if 'var _locationAddress = "' in line2:
                addinfo = line2.split('var _locationAddress = "')[1].split('"')[0]
                if addinfo.count(",") == 3:
                    add = (
                        addinfo.split(",")[0].strip()
                        + " "
                        + addinfo.split(",")[1].strip()
                    )
                else:
                    add = addinfo.split(",")[0].strip()
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
        logger.info(f"[{idx2}] Phone: {phone}")
        name = name.replace("\\u0026", "&")
        if hours == "":
            logger.info("Hours found to be empty")
            hurl = loc.replace("/#", "") + "/Website/Hours"
            logger.info(f"[{idx2}] Pulling Hours for {hurl}")
            try:
                r3 = get_response(hurl, headers_)
                lines2 = r3.iter_lines()
                for line3 in lines2:
                    if "day</td>" in line3:
                        day = line3.split(">")[1].split("<")[0]
                    if '"text-right">' in line3:
                        if '<td class="text-right">Closed' in line3:
                            day = day + ": Closed"
                        else:
                            g = next(lines2)
                            day = (
                                day
                                + ": "
                                + g.replace("\r", "")
                                .replace("\t", "")
                                .replace("\n", "")
                                .strip()
                            )
                            if hours == "":
                                hours = day
                            else:
                                hours = hours + "; " + day
            except:
                hours = "Temporarily Closed"
        if "3948 S Peoria" in add:
            hours = "Monday-Friday: 7:00AM-1:00PM, Saturday and Sunday: 6:00AM-2:00PM"
        if "1616 N May Ave" in add:
            hours = "Monday - Sunday: 6:30 AM - 2:00 PM"
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
    loc = "https://mcallen.orderjimmysegg.com/"
    name = "McAllen, TX"
    add = "4100 N. 10th St."
    city = "McAllen"
    state = "TX"
    zc = "78504"
    phone = "<MISSING>"
    store = "<MISSING>"
    hours = "Sun-Sat: 6am-2pm"
    lat = "<MISSING>"
    lng = "<MISSING>"
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
    loc = "<MISSING>"
    name = "Mission, TX"
    add = "614 N. Shary Road"
    city = "Mission"
    state = "TX"
    zc = "78572"
    phone = "<MISSING>"
    store = "<MISSING>"
    hours = "Sun-Sat: 6am-2pm"
    lat = "<MISSING>"
    lng = "<MISSING>"
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
    logger.info("Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
    logger.info("Scrape Finished")


if __name__ == "__main__":
    scrape()
