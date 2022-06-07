from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("aamco_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    canada = [
        "ON",
        "SK",
        "AB",
        "NB",
        "NL",
        "PQ",
        "QC",
        "NS",
        "BC",
        "PEI",
        "PE",
        "NU",
        "YK",
    ]
    url = "https://www.aamco.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.aamco.com/Auto-Repair-Center/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") > 4:
                locs.append(lurl)
    for loc in locs:
        try:
            logger.info(("Pulling Location %s..." % loc))
            website = "aamco.com"
            name = ""
            store = "<MISSING>"
            lat = ""
            lng = ""
            hours = ""
            phone = ""
            add = ""
            city = ""
            zc = ""
            typ = "<MISSING>"
            state = loc.split("https://www.aamco.com/Auto-Repair-Center/")[1].split(
                "/"
            )[0]
            if state in canada:
                country = "CA"
            else:
                country = "US"
            hours = ""
            r2 = session.get(loc, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                if "day</span></p>" in line2:
                    hrs = line2.split("<span>")[1].split("<")[0]
                    next(lines)
                    next(lines)
                    g = next(lines)
                    if "<span>" not in g:
                        g = next(lines)
                    hrs = hrs + ": " + g.split("<span>")[1].split("<")[0]
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
                if '<h2 class="title02">' in line2 and name == "":
                    name = line2.split('<h2 class="title02">')[1].split("<")[0].strip()
                if '<span class="smalltxt">Address</span>' in line2:
                    g = next(lines)
                    if "IL/Waukegan/S-Green-Bay-Rd" in loc:
                        add = "69 South Green Bay Road"
                        city = "Waukegan"
                        zc = "60085"
                    elif "Medford-Ave," in loc:
                        add = "638 Medford Ave. Rt 112"
                        city = "Patchogue"
                        state = "NY"
                        zc = "11772"
                    else:
                        if "," not in g:
                            g = next(lines)
                        addinfo = (
                            g.split("<")[0]
                            .strip()
                            .replace("\t", "")
                            .replace(", Canada", "")
                        )
                        add = addinfo.split(",")[0]
                        city = addinfo.split(",")[1].strip()
                        try:
                            zc = addinfo.rsplit(",", 1)[1].strip().split(" ", 1)[1]
                        except:
                            state = loc.split("/")[4]
                            zc = addinfo.rsplit(",", 1)[1].strip()
                if "Phone</span>" in line2:
                    try:
                        phone = next(lines).split('">')[1].split("<")[0]
                    except:
                        phone = "<MISSING>"
                if "var uluru = { lat:" in line2:
                    lat = line2.split("var uluru = { lat:")[1].split(",")[0].strip()
                    lng = line2.split("lng:")[1].split("}")[0].strip()
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if city == "#102":
                city = "El Paso"
                add = "1407 Lomaland Dr. #102"
            if city == "#13":
                city = "Santa Clarita"
                add = "25845 Railroad Avenue #13"
            if city == "#A":
                city = "Willoughby"
                add = "36705 Euclid Ave. #A"
            if city == "Harbor City":
                zc = "90710"
            if "Eglinton" in add or "Manitou" in add or "Hopkins St" in add:
                state = "ON"
                zc = "<MISSING>"
            if "/Canada/" in loc:
                country = "CA"
            city = loc.split("/")[5].replace("-", " ")
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/Canada/Kitchener/Manitou-Drive,-Unit-4"
            ):
                zc = "N2C 1L4"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/Canada/Scarborough/Eglinton-Ave-E"
            ):
                zc = "M1J 2E5"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/Canada/Whitby/Hopkins-Street"
            ):
                zc = "L1N 2C1"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/CA/San-Diego/Morena-Boulevard"
            ):
                zc = "<MISSING>"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/ID/Twin-Falls/Cheney-Drive"
            ):
                zc = "83301"
            if loc == "https://www.aamco.com/Auto-Repair-Center/TX/Houston/Highway-6-N":
                zc = "77084"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/TX/Stephenville/N-Floral-St"
            ):
                zc = "<MISSING>"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/FL/Lauderhill/N-University-Drive"
            ):
                zc = "33351"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/IL/Chicago/4710-South-Halsted-Street"
            ):
                zc = "60609"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/MS/Jackson/Briarwood-Dr"
            ):
                zc = "39206"
            if (
                loc
                == "https://www.aamco.com/Auto-Repair-Center/VA/Winchester/S-Loudoun-St"
            ):
                zc = "22601"
            if add != "":
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
