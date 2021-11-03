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

logger = SgLogSetup().get_logger("ford_co_uk")


def fetch_data():
    infos = []
    cities = [
        "50,-1",
        "51,-1",
        "52,-1",
        "53,-1",
        "54,-1",
        "55,-1",
        "56,-1",
        "57,-1",
        "58,-1",
        "50,0",
        "51,0",
        "52,0",
        "53,0",
        "54,0",
        "55,0",
        "56,0",
        "57,0",
        "58,0",
        "50,1",
        "51,1",
        "52,1",
        "53,1",
        "54,1",
        "55,1",
        "56,1",
        "57,1",
        "58,1",
        "50,-2",
        "51,-2",
        "52,-2",
        "53,-2",
        "54,-2",
        "55,-2",
        "56,-2",
        "57,-2",
        "58,-2",
        "50,-3",
        "51,-3",
        "52,-3",
        "53,-3",
        "54,-3",
        "55,-3",
        "56,-3",
        "57,-3",
        "58,-3",
        "50,-4",
        "51,-4",
        "52,-4",
        "53,-4",
        "54,-4",
        "55,-4",
        "56,-4",
        "57,-4",
        "58,-4",
        "50,-5",
        "51,-5",
        "52,-5",
        "53,-5",
        "54,-5",
        "55,-5",
        "56,-5",
        "57,-5",
        "58,-5",
    ]
    for loc in cities:
        logger.info(loc)
        llat = loc.split(",")[0]
        llng = loc.split(",")[1]
        url = (
            "https://spatial.virtualearth.net/REST/v1/data/1652026ff3b247cd9d1f4cc12b9a080b/FordEuropeDealers_Transition/Dealer?spatialFilter=nearby("
            + llat
            + ","
            + llng
            + ",160.934)&$select=*,__Distance&$filter=CountryCode%20Eq%20%27GBR%27&$top=250&$format=json&key=Al1EdZ_aW5T6XNlr-BJxCw1l4KaA0tmXFI_eTl1RITyYptWUS0qit_MprtcG7w2F&Jsonp=collectResults&$skip=0"
        )
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"DealerID":"' in line:
                items = line.split(',"EntityID":"')
                for item in items:
                    if '"DealerID":"' in item:
                        website = "ford.co.uk"
                        typ = item.split('"Brand":"')[1].split('"')[0]
                        lat = item.split('"Latitude":')[1].split(",")[0]
                        lng = item.split('"Longitude":')[1].split(",")[0]
                        name = item.split('"DealerName":"')[1].split('"')[0]
                        add = (
                            item.split('"AddressLine1":"')[1].split('"')[0]
                            + " "
                            + item.split('"AddressLine2":"')[1].split('"')[0]
                            + " "
                            + item.split('"AddressLine3":"')[1].split('"')[0]
                        )
                        add = add.strip()
                        city = item.split('"Locality":"')[1].split('"')[0]
                        country = "GB"
                        loc = (
                            "https://www.ford.co.uk/dealer-locator#/dealer/"
                            + item.split('"')[0]
                        )
                        state = "<MISSING>"
                        zc = item.split('"PostCode":"')[1].split('"')[0]
                        store = item.split('"DealerID":"')[1].split('"')[0]
                        phone = item.split('"PrimaryPhone":"')[1].split('"')[0]
                        hours = "<MISSING>"
                        if phone == "":
                            phone = "<MISSING>"
                        if city == "":
                            city = "<MISSING>"
                        if add == "":
                            add = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
                        if '"SalesMondayOpenTime":""' not in item:
                            hours = (
                                "Mon: "
                                + item.split('"SalesMondayOpenTime":"')[1].split('"')[0]
                                + "-"
                                + item.split('"SalesMondayCloseTime":"')[1].split('"')[
                                    0
                                ]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Tue: "
                                + item.split('"SalesTuesdayOpenTime":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('"SalesTuesdayCloseTime":"')[1].split('"')[
                                    0
                                ]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Wed: "
                                + item.split('"SalesWednesdayOpenTime":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + item.split('"SalesWednesdayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Thu: "
                                + item.split('"SalesThursdayOpenTime":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('"SalesThursdayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Fri: "
                                + item.split('"SalesFridayOpenTime":"')[1].split('"')[0]
                                + "-"
                                + item.split('"SalesFridayCloseTime":"')[1].split('"')[
                                    0
                                ]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Sat: "
                                + item.split('"SalesSaturdayOpenTime":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('"SalesSaturdayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Sun: "
                                + item.split('"SalesSundayOpenTime":"')[1].split('"')[0]
                                + "-"
                                + item.split('"SalesSundayCloseTime":"')[1].split('"')[
                                    0
                                ]
                            )
                        if (
                            '"ServiceMondayOpenTime":""' not in item
                            and hours == "<MISSING>"
                        ):
                            hours = (
                                "Mon: "
                                + item.split('"ServiceMondayOpenTime":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('"ServiceMondayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Tue: "
                                + item.split('"ServiceTuesdayOpenTime":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + item.split('"ServiceTuesdayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Wed: "
                                + item.split('"ServiceWednesdayOpenTime":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + item.split('"ServiceWednesdayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Thu: "
                                + item.split('"ServiceThursdayOpenTime":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + item.split('"ServiceThursdayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Fri: "
                                + item.split('"ServiceFridayOpenTime":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('"ServiceFridayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Sat: "
                                + item.split('"ServiceSaturdayOpenTime":"')[1].split(
                                    '"'
                                )[0]
                                + "-"
                                + item.split('"ServiceSaturdayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                            hours = (
                                hours
                                + "; "
                                + "Sun: "
                                + item.split('"ServiceSundayOpenTime":"')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + item.split('"ServiceSundayCloseTime":"')[1].split(
                                    '"'
                                )[0]
                            )
                        addinfo = lat + "|" + lng
                        if addinfo not in infos:
                            infos.append(addinfo)
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
