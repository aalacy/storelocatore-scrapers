from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

headers = {
    "authority": "www.unitedcheckcashing.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

logger = SgLogSetup().get_logger("unitedcheckcashing_com")


def fetch_data():
    url = "http://www.unitedcheckcashing.com/locations"
    locs = []
    with SgRequests() as session:
        r = session.get(url, headers=headers)
        website = "unitedcheckcashing.com"
        typ = "<MISSING>"
        country = "US"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line)
            if 'class="detail_location" ><a href="store/' in line:
                locs.append(
                    "https://www.unitedcheckcashing.com/"
                    + line.split('href="')[1].split('"')[0]
                )
        for loc in locs:
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = loc.rsplit("/", 1)[1]
            phone = ""
            lat = ""
            lng = ""
            hours = ""
            r2 = session.get(loc, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                line2 = str(line2)
                if "<h2>" in line2:
                    name = line2.split(">")[1].split("<")[0]
                    logger.info(name)
                if 'location_center_left">' in line2:
                    next(lines)
                    g = next(lines)
                    g = str(g)
                    add = g.split(">")[1].split("<")[0]
                    g = next(lines)
                    g = str(g)
                    g = g.split(">")[1].split("<")[0].strip()
                    city = g.split(",")[0]
                    state = g.split(",")[1].strip().split(" ")[0]
                    zc = g.rsplit(" ", 1)[1]
                if "Phone" in line2 and 'phone-call inlinelnk" href="tel:' in line2:
                    phone = line2.split('phone-call inlinelnk" href="tel:')[1].split(
                        '"'
                    )[0]
                if 'onclick="loadmap("' in line2:
                    lat = line2.split('onclick="loadmap("')[1].split('"')[0]
                    lng = (
                        line2.split('onclick="loadmap("')[1]
                        .split(',"')[1]
                        .split('"')[0]
                    )
                if ".</div><div class=" in line2:
                    hrs = (
                        line2.split('xs-4">')[1].split("<")[0]
                        + ": "
                        + line2.split('col-xs-8">')[1].split("<")[0]
                    )
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs

            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                store_number=store,
                phone=phone,
                location_type=typ,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
