# -*- coding: cp1252 -*-
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import unicodedata

logger = SgLogSetup().get_logger("jiffylubeqc_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
}
headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://jiffylubeqc.com/succursales/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if (
            'menu-item-depth-1" value="https://jiffylubeqc.com/succursales/' in line
            and "Trouver votre su" not in line
            and "Calendrier" not in line
        ):
            locs.append(
                "https://jiffylubeqc.com/succursales/"
                + line.split(
                    'menu-item-depth-1" value="https://jiffylubeqc.com/succursales/'
                )[1].split('"')[0]
            )
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        zc = ""
        city = ""
        website = "jiffylubeqc.com"
        country = "CA"
        state = "QC"
        typ = "<MISSING>"
        HFound = False
        hours = ""
        add = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        phone = ""
        store = "<MISSING>"
        name = ""
        r2 = session.get(loc, headers=headers2)
        lines = r2.iter_lines()
        for line2 in lines:
            if "<p><strong>" in line2:
                name = line2.split("<p><strong>")[1].split("<")[0]
                g = next(lines)
                h = next(lines)
                add = g.split("<")[0]
                city = name.split("Jiffy lube")[1].strip()
                zc = h.split(",")[2].split("<")[0].strip()
            if "new google.maps.LatLng(" in line2:
                lat = line2.split("new google.maps.LatLng(")[1].split(",")[0]
                lng = (
                    line2.split("new google.maps.LatLng(")[1]
                    .split(",")[1]
                    .split(")")[0]
                )
            if "phone : <strong>" in line2:
                phone = line2.split("phone : <strong>")[1].split("<")[0]
            if "<h2>Heures d&rsquo;ouverture</h2>" in line2:
                HFound = True
            if HFound and "<h2>Cartes" in line2:
                HFound = False
            if HFound and "<h2>" not in line2:
                hrs = (
                    line2.replace("\r", "").replace("\t", "").replace("\n", "").strip()
                )
                hrs = hrs.replace("<br />", "").replace("<p>", "").replace("</p>", "")
                hrs = hrs.replace("<strong>", "").replace("</strong>", "")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"

        hours = (
            unicodedata.normalize("NFD", hours)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        hours = (
            hours.replace(" a ", " - ")
            .replace("Du ", "")
            .replace("Lundi au Vendredi", "Mon-Fri")
            .replace("Samedi", "Saturday")
            .replace("Dimanche", "Sunday")
            .replace("FERME", "Closed")
            .replace("à", "to")
            .replace("Ferme", "Closed")
            .replace(" et ", " and ")
        )
        logger.info(f"HOO: {hours}")
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
