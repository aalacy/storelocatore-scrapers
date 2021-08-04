from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("calibercollision_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://calibercollision.com/api/locations"
    r = session.get(url, headers=headers)
    website = "calibercollision.com"
    typ = "<MISSING>"
    country = "US"
    for item in json.loads(r.content)["entries"]:
        name = item["title"]
        try:
            hours = str(item["hours"])
        except:
            hours = "<MISSING>"
        hours = (
            hours.replace("<br />", "; ")
            .replace("\n", "")
            .replace("<br/>", "; ")
            .replace("<br>", "; ")
        )
        add = item["address_info"][0]["address"].replace('"', "'")
        city = item["address_info"][0]["city"]
        state = item["address_info"][0]["state_province"]
        zc = item["address_info"][0]["zip"]
        try:
            lat = item["address_info"][0]["latitude"]
            lng = item["address_info"][0]["longitude"]
        except:
            lat = "<MISSING>"
            lng = "<MISSING>"
        try:
            phone = item["address_info"][0]["phone"]
        except:
            phone = "<MISSING>"
        loc = (
            "https://calibercollision.com/locate-a-caliber-collision-center/"
            + item["slug"]
        )
        try:
            store = item["location_id"]
        except:
            store = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if hours == "<MISSING>":
            r2 = session.get(loc, headers=headers)
            hours = ""
            logger.info(loc)
            try:
                lines = r2.iter_lines()
                alltext = str(r2.content).replace("\r", "").replace("\n", "")
                if '<span class="Hours_day' in alltext:
                    items = alltext.split('<span class="Hours_day')
                    for item in items:
                        if "<html>" not in item:
                            hrs = (
                                item.split('">')[1].split("<")[0]
                                + ": "
                                + item.split("</span><span>")[1].split("<")[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                if hours == "":
                    for line2 in lines:
                        line2 = str(line2.decode("utf-8"))
                        if '<span class="d-block pt-3 italic newtime">' in line2:
                            g = next(lines)
                            g = str(g.decode("utf-8"))
                            if "By Appointment Only" in g:
                                hours = "By Appointment Only"
                            else:
                                g = next(lines)
                                g = str(g.decode("utf-8"))
                                while "m" not in g:
                                    g = next(lines)
                                    g = str(g.decode("utf-8"))
                                hours = (
                                    g.strip()
                                    .replace("\t", "")
                                    .replace("\r", "")
                                    .replace("\n", "")
                                )
                                g = next(lines)
                                g = str(g.decode("utf-8"))
                                if "m" in g:
                                    hours = (
                                        hours
                                        + "; "
                                        + g.split(">")[1]
                                        .strip()
                                        .replace("\t", "")
                                        .replace("\r", "")
                                        .replace("\n", "")
                                        .replace("&amp;", "&")
                                    )
                                hours = hours.replace("<br/>", "; ")
                                hours = (
                                    hours.replace("  ", " ")
                                    .replace("  ", " ")
                                    .replace("  ", " ")
                                    .replace("  ", " ")
                                    .replace("  ", " ")
                                    .replace("  ", " ")
                                    .replace("  ", " ")
                                )
                                hours = hours.replace("\t", "")
                                hours = hours.replace(" ;", ";")
            except:
                pass
            if hours == "":
                hours = "<MISSING>"
        hours = (
            hours.replace("\n", "")
            .replace("\\n", "")
            .replace("\t", "")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
        )
        if "no-location" not in loc:
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
