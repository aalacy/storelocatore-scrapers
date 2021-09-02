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

logger = SgLogSetup().get_logger("timhortons_com")


def fetch_data():
    ids = []
    lngs = [
        "-60,-70",
        "-70,-75",
        "-75,-80",
        "-80,-85",
        "-85,-90",
        "-90,-95",
        "-95,-100",
        "-100,-110",
        "-110,-120",
        "-120,-130",
        "-130,-140",
    ]
    for coord in lngs:
        logger.info(coord)
        lng1 = coord.split(",")[0]
        lng2 = coord.split(",")[1]
        url = (
            "https://czqk28jt.apicdn.sanity.io/v1/data/query/prod_th_us?query=*%5B%20_type%20%3D%3D%20%27restaurant%27%20%26%26%20environment%20%3D%3D%20%24environment%20%26%26%20!(%24appEnvironemnt%20in%20coalesce(hideInEnvironments%2C%20%5B%5D))%20%26%26%20latitude%20%3E%20%24minLat%20%26%26%20latitude%20%3C%20%24maxLat%20%26%26%20longitude%20%3E%20%24minLng%20%26%26%20longitude%20%3C%20%24maxLng%20%26%26%20status%20%3D%3D%20%24status%20%5D%20%7Corder((%24userLat%20-%20latitude)%20**%202%20%2B%20(%24userLng%20-%20longitude)%20**%202)%5B%24offset...(%24offset%20%2B%20%24limit)%5D%20%7B_id%2CdeliveryHours%2CdiningRoomHours%2CcurbsideHours%2CdrinkStationType%2CdriveThruHours%2CdriveThruLaneType%2Cemail%2CfranchiseGroupId%2CfranchiseGroupName%2CfrontCounterClosed%2ChasBreakfast%2ChasBurgersForBreakfast%2ChasCurbside%2ChasDineIn%2ChasCatering%2ChasDelivery%2ChasDriveThru%2ChasMobileOrdering%2ChasParking%2ChasPlayground%2ChasTakeOut%2ChasWifi%2Clatitude%2Clongitude%2CmobileOrderingStatus%2Cname%2Cnumber%2CparkingType%2CphoneNumber%2CphysicalAddress%2CplaygroundType%2Cpos%2CposRestaurantId%2CrestaurantPosData-%3E%7B_id%2C%20lastHeartbeatTimestamp%2C%20heartbeatStatus%2C%20heartbeatOverride%7D%2Cstatus%2CrestaurantImage%7B...%2C%20asset-%3E%7D%7D&%24appEnvironemnt=%22prod%22&%24environment=%22prod%22&%24limit=2000&%24maxLat=70.38222283530336&%24maxLng="
            + lng1
            + "&%24minLat=10.2805901091501&%24minLng="
            + lng2
            + "&%24offset=0&%24status=%22Open%22&%24userLat=42.331427&%24userLng=-83.0457538"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"_id":"restaurant_' in line:
                items = line.split('{"_id":"restaurant_')
                for item in items:
                    if '{"ms":' not in item:
                        store = item.split('"')[0]
                        loc = (
                            "https://www.timhortons.com/store-locator/store/restaurant_"
                            + store
                        )
                        website = "timhortons.com"
                        name = item.split('"name":"')[1].split('"')[0]
                        add = (
                            item.split('"address1":"')[1].split('"')[0]
                            + " "
                            + item.split('"address2":"')[1].split('"')[0]
                        )
                        add = add.strip()
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"stateProvince":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        country = item.split('"country":"')[1].split('"')[0]
                        if country == "Canada":
                            country = "CA"
                        else:
                            country = "US"
                        typ = "<MISSING>"
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        phone = item.split('"phoneNumber":"')[1].split('"')[0]
                        if phone == "":
                            phone = "<MISSING>"
                        hours = ""
                        dthours = ""
                        if '"driveThruHours":{"_type":"hoursOfOperation",' in item:
                            days = item.split(
                                '"driveThruHours":{"_type":"hoursOfOperation",'
                            )[1].split("}")[0]
                            try:
                                dthours = (
                                    "Mon: "
                                    + days.split('"monOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"monClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                dthours = (
                                    dthours
                                    + "; Tue: "
                                    + days.split('"tueOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"tueClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                dthours = (
                                    dthours
                                    + "; Wed: "
                                    + days.split('"wedOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"wedClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                dthours = (
                                    dthours
                                    + "; Thu: "
                                    + days.split('"thrOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"thrClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                dthours = (
                                    dthours
                                    + "; Fri: "
                                    + days.split('"friOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"friClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                dthours = (
                                    dthours
                                    + "; Sat: "
                                    + days.split('"satOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"satClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                dthours = (
                                    dthours
                                    + "; Sun: "
                                    + days.split('"sunOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"sunClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                            except:
                                pass
                        if '"diningRoomHours":{"_type":"hoursOfOperation"' in item:
                            days = item.split(
                                '"diningRoomHours":{"_type":"hoursOfOperation"'
                            )[1].split("}")[0]
                            try:
                                hours = (
                                    "Mon: "
                                    + days.split('"monOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"monClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Tue: "
                                    + days.split('"tueOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"tueClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Wed: "
                                    + days.split('"wedOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"wedClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Thu: "
                                    + days.split('"thrOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"thrClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Fri: "
                                    + days.split('"friOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"friClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Sat: "
                                    + days.split('"satOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"satClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                                hours = (
                                    hours
                                    + "; Sun: "
                                    + days.split('"sunOpen":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                    + "-"
                                    + days.split('"sunClose":"')[1]
                                    .split(" ")[1]
                                    .split(':00"')[0]
                                )
                            except:
                                pass
                        if hours == "":
                            hours = dthours
                        if hours == "":
                            hours = "<CLOSED>"
                        if store not in ids:
                            ids.append(store)
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
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
