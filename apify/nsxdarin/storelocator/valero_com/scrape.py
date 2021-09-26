from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("valero_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}


def fetch_data():
    url = "https://locations.valero.com/en-us/Home/SearchForLocations"
    for coord in range(-60, -170, -2):
        for latcoord in range(70, 10, -2):
            logger.info(
                str(coord)
                + "-"
                + str(coord - 2)
                + "; "
                + str(latcoord)
                + ","
                + str(latcoord - 2)
            )
            payload = {
                "NEBound_Lat": str(latcoord),
                "NEBound_Long": str(coord),
                "SWBound_Lat": str(latcoord - 2),
                "SWBound_Long": str(coord - 2),
                "center_Lat": "",
                "center_Long": "",
            }

            r = session.post(url, headers=headers, data=payload)
            for line in r.iter_lines():
                line = str(line.decode("utf-8"))
                if '"Name":"' in line:
                    items = line.split('"Name":"')
                    for item in items:
                        if '"DirectionsURL":"' in item:
                            website = "valero.com"
                            country = "US"
                            zc = item.split('"PostalCode":"')[1].split('"')[0]
                            phone = item.split('"Phone":"')[1].split('"')[0]
                            lat = item.split('"Latitude":')[1].split(",")[0]
                            lng = item.split('"Longitude":')[1].split(",")[0]
                            typ = "<MISSING>"
                            name = (
                                item.split('"')[0]
                                .replace("\\u0026", "&")
                                .replace("\\u0027", "'")
                            )
                            store = item.split('"LocationDetails":[{"LocationID":"')[
                                1
                            ].split('"')[0]
                            purl = (
                                "https://locations.valero.com/en-us/LocationDetails/Index/"
                                + item.split('"DetailPageUrlID":"')[1].split('"')[0]
                                + "/"
                                + store
                            )
                            add = item.split('"AddressLine1":"')[1].split('"')[0]
                            try:
                                add = (
                                    add
                                    + " "
                                    + item.split('"AddressLine2":"')[1].split('"')[0]
                                )
                            except:
                                pass
                            city = item.split('"City":"')[1].split('"')[0]
                            state = item.split('"State":"')[1].split('"')[0]
                            hours = "<MISSING>"
                            if phone == "":
                                phone = "<MISSING>"
                            if phone == "0":
                                phone = "<MISSING>"
                            if (
                                "1" not in phone
                                and "2" not in phone
                                and "3" not in phone
                                and "4" not in phone
                                and "5" not in phone
                                and "6" not in phone
                                and "7" not in phone
                                and "8" not in phone
                                and "9" not in phone
                            ):
                                phone = "<MISSING>"
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
