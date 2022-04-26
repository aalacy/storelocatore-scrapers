from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("bekins_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.bekins.com/agent-sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines():
        if (
            "<loc>https://www.bekins.com/find-a-local-agent/agents/" in line
            and "<loc>https://www.bekins.com/find-a-local-agent/agents/<" not in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        req = session.get(loc, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        try:
            name = list(
                base.find(
                    class_="u-textAlignCenter u-paddingTop4gu u-marginBottom0gu"
                ).stripped_strings
            )[0]
            raw_address = list(
                base.find(
                    class_="u-textAlignCenter u-paddingTop4gu u-marginBottom0gu"
                ).stripped_strings
            )[1].split(",")
        except:
            continue
        add = " ".join(raw_address[:-2])
        city = raw_address[-2].strip()
        state = raw_address[-1].split()[0]
        zc = raw_address[-1].split()[1]
        phone = (
            base.find(string="Call Us").find_previous("a")["href"].replace("tel:", "")
        )
        website = "bekins.com"
        typ = ""
        country = "US"
        store = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        if state != "":
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
