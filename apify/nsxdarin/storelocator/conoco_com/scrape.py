from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("conoco_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

usstates = [
    "AK",
    "AL",
    "AR",
    "AS",
    "AZ",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "GA",
    "GU",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MP",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "PR",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UM",
    "UT",
    "VA",
    "VI",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
]


def fetch_data():
    for x in range(10, 65, 2):
        for y in range(-60, -170, -2):
            logger.info(str(x) + "," + str(y))
            url = (
                "https://spatial.virtualearth.net/REST/v1/data/a1ed23772f5f4994a096eaa782d07cfb/US_BrandedSites/Sites?spatialFilter=nearby("
                + str(x)
                + ","
                + str(y)
                + ",1000)&$filter=Confidence%20Eq%20%27High%27%20And%20(EntityType%20Eq%20%27Address%27%20Or%20EntityType%20Eq%20%27RoadIntersection%27)%20AND%20(Brand%20eq%20%27CON%27%20OR%20Brand%20Eq%20%27CON%27)&$format=json&$inlinecount=allpages&$select=*,__Distance&key=AqlID-ciQMxSAGsGXCatVwPLpgJOenb60MsckJMpLhyd0mxjEwEYN3ELSUCn2cQQ&$top=1000"
            )
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '"uri":"' in line:
                    items = line.split('"uri":"')
                    for item in items:
                        if '"EntityID":"' in item:
                            website = "conoco.com"
                            typ = item.split('"Brand":"')[1].split('"')[0]
                            store = item.split('"EntityID":"')[1].split('"')[0]
                            add = item.split('"AddressLine":"')[1].split('"')[0]
                            state = item.split('"AdminDistrict":"')[1].split('"')[0]
                            country = item.split('"CountryRegion":"')[1].split('"')[0]
                            city = item.split('"Locality":"')[1].split('"')[0]
                            zc = item.split('"PostalCode":"')[1].split('"')[0]
                            lat = item.split('"Latitude":')[1].split(",")[0]
                            lng = item.split('"Longitude":')[1].split(",")[0]
                            phone = item.split('"Phone":"')[1].split('"')[0]
                            name = (
                                item.split('"Name":"')[1]
                                .split('"')[0]
                                .replace("\\/", "/")
                            )
                            loc = (
                                "https://www.conoco.com/station/"
                                + typ
                                + "-"
                                + name.replace(" ", "-")
                                + "-"
                                + store
                            )
                            hours = "<MISSING>"
                            if phone == "":
                                phone = "<MISSING>"
                            if state in usstates:
                                country = "US"
                            else:
                                if int(lat.split(".")[0]) >= 45:
                                    country = "CA"
                                else:
                                    country = "MX"
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
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
