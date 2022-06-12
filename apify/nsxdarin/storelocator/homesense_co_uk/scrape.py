from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("homesense_co_uk")


def fetch_data():
    locs = ["https://www.homesense.com/stores/Cork"]
    cities = [
        "London",
        "Birmingham",
        "Glasgow",
        "Liverpool",
        "Blanchardstown",
        "Bristol",
        "Manchester",
        "Sheffield",
        "Leeds",
        "Edinburgh",
        "Leicester",
        "Coventry",
        "Bradford",
        "Cardiff",
        "Belfast",
        "Nottingham",
        "Kingston upon Hull",
        "Newcastle upon Tyne",
        "Stoke on Trent",
        "Southampton",
        "Derby",
        "Portsmouth",
        "Brighton and Hove",
        "Plymouth",
        "Northampton",
        "Reading",
        "Luton",
        "Wolverhampton",
        "Bournemouth",
        "Aberdeen",
        "Bolton",
        "Norwich",
        "Swindon",
        "Swansea",
        "Milton Keynes",
        "Southend on Sea",
        "Middlesbrough",
        "Sunderland",
        "Peterborough",
        "Warrington",
        "Oxford",
        "Huddersfield",
        "Slough",
        "York",
        "Poole",
        "Cambridge",
        "Dundee",
        "Ipswich",
        "Telford",
        "Gloucester",
        "Blackpool",
        "Birkenhead",
        "Watford",
        "Sale",
        "Colchester",
        "Newport",
        "Solihull",
        "High Wycombe",
        "Exeter",
        "Gateshead",
        "Cheltenham",
        "Blackburn",
        "Maidstone",
        "Chelmsford",
        "Basildon",
        "Salford",
        "Basingstoke",
        "Worthing",
        "Eastbourne",
        "Doncaster",
        "Crawley",
        "Rotherham",
        "Rochdale",
        "Stockport",
        "Gillingham",
        "Sutton Coldfield",
        "Woking",
        "Wigan",
        "Lincoln",
        "St Helens",
        "Oldham",
        "Worcester",
        "Wakefield",
        "Hemel Hempstead",
        "Bath",
        "Preston",
        "Rayleigh",
        "Barnsley",
        "Stevenage",
        "Southport",
        "Hastings",
        "Bedford",
        "Darlington",
        "Halifax",
        "Hartlepool",
        "Chesterfield",
        "Grimsby",
        "Nuneaton",
        "Weston super Mare",
        "Chester",
        "St Albans",
        "Harlow",
        "Guildford",
        "Stockton on Tees",
        "Aylesbury",
        "Derry",
        "Bracknell",
        "Dudley",
        "Redditch",
        "Batley",
        "Scunthorpe",
        "Burnley",
        "Eastleigh",
        "Chatham",
        "Mansfield",
        "Bury",
        "Newcastle under Lyme",
        "Paisley",
        "West Bromwich",
        "South Shields",
        "Carlisle",
        "East Kilbride",
    ]
    website = "homesense.co.uk"
    typ = "<MISSING>"
    country = "GB"
    for cname in cities:
        url = "https://www.homesense.com/find-a-store?address=" + cname
        r = session.get(url, headers=headers)
        r = session.get("https://www.homesense.com/search-results", headers=headers)
        logger.info(cname)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if "2view-store-info\\u0022 href=\\u0022\\" in line:
                items = line.split("2view-store-info\\u0022 href=\\u0022\\")
                for item in items:
                    if "EView store info" in item:
                        lurl = "https://www.homesense.com" + item.split("\\u0022")[
                            0
                        ].replace("\\", "").replace(" ", "_")
                        lurl = (
                            lurl.replace("%20", "_")
                            .replace("%28", "")
                            .replace("%29", "")
                        )
                        if lurl not in locs:
                            locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = loc.rsplit("/", 1)[1].replace("%20", " ")
        state = "<MISSING>"
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2 and name == "":
                name = line2.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split("|")[0].strip()
            if hours == "" and '<span itemprop="openingHours" datetime="">' in line2:
                hours = line2.split('<span itemprop="openingHours" datetime="">')[
                    1
                ].split("<")[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if add == "" and 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if 'itemprop="addressLocality">' in line2 and city == "":
                add = (
                    add
                    + " "
                    + line2.split('itemprop="addressLocality">')[1].split("<")[0]
                )
            if 'itemprop="zipCode">' in line2 and zc == "":
                zc = line2.split('itemprop="zipCode">')[1].split("<")[0]
            if store == "" and 'data-store-id="' in line2:
                store = line2.split('data-store-id="')[1].split('"')[0]
            if phone == "" and '<p itemprop="telephone">' in line2:
                phone = line2.split('<p itemprop="telephone">')[1].split("<")[0]
        hours = hours.replace(" : ", ": ")
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "%" in city:
            city = city.split("%")[0]
        city = city.strip()
        if "Manchester" in city:
            city = "Manchester"
        if "Staples" in name:
            city = "London"
        city = city.replace("Hedge_End", "Hedge End")
        city = city.replace("Kingston_Park", "Kingston Park")
        city = city.replace("Merthyr_Tydfil", "Merthyr Tydfil")
        city = city.replace("Fort_Kinnaird", "Fort Kinnaird")
        city = city.replace("Milton_Keynes", "Milton Keynes")
        city = city.replace("Tunbridge_Wells", "Tunbridge Wells")
        if "_" in city:
            city = city.split("_")[0]
        if "stores/Cork" in loc:
            country = "IE"
            add = "The Capitol 14-23 Grand Parade"
            state = "<MISSING>"
            name = "Cork"
            zc = "T12 RF85"
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
