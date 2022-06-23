from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("burgerking_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():
    url = "https://www.burgerking.ca/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.burgerking.ca/store-locator/store/" in line:
            items = line.split("<loc>https://www.burgerking.ca/store-locator/store/")
            for item in items:
                if (
                    "<?xml version" not in item
                    and "test-" not in item
                    and "13101" not in item
                ):
                    locs.append(
                        "https://www.burgerking.ca/store-locator/store/"
                        + item.split("<")[0]
                    )
    for loc in locs:
        store = loc.split("/store/")[1].split("/")[0]
        lurl = (
            "https://czqk28jt.apicdn.sanity.io/v1/graphql/prod_bk_ca/default?operationName=GetRestaurants&variables=%7B%22filter%22%3A%7B%22number%22%3A%22"
            + store
            + "%22%7D%2C%22limit%22%3A1%7D&query=query+GetRestaurants%28%24filter%3ARestaurantFilter%2C%24limit%3AInt%29%7BallRestaurants%28where%3A%24filter%2Climit%3A%24limit%29%7B...RestaurantFragment+__typename%7D%7Dfragment+RestaurantFragment+on+Restaurant%7B_id+environment+chaseMerchantId+deliveryHours%7B...HoursFragment+__typename%7DdiningRoomHours%7B...HoursFragment+__typename%7DcurbsideHours%7B...HoursFragment+__typename%7DdriveThruHours%7B...HoursFragment+__typename%7DdrinkStationType+driveThruLaneType+email+franchiseGroupId+franchiseGroupName+frontCounterClosed+hasBreakfast+hasBurgersForBreakfast+hasCurbside+hasDineIn+hasCatering+hasDelivery+hasDriveThru+hasMobileOrdering+hasParking+hasPlayground+hasTakeOut+hasWifi+isDarkKitchen+latitude+longitude+mobileOrderingStatus+name+number+parkingType+phoneNumber+playgroundType+pos%7B_type+vendor+__typename%7DphysicalAddress%7B_type+address1+address2+city+country+postalCode+stateProvince+__typename%7DposRestaurantId+restaurantPosData%7B_id+__typename%7Dstatus+restaurantImage%7Bhotspot%7Bwidth+height+x+y+__typename%7Dcrop%7Btop+bottom+left+right+__typename%7Dasset%7B...ImageAssetFragment+__typename%7D__typename%7Damenities%7Bname%7Ben+__typename%7Dicon%7Basset%7B...ImageAssetFragment+__typename%7D__typename%7D__typename%7D__typename%7Dfragment+HoursFragment+on+HoursOfOperation%7B_type+friClose+friOpen+monClose+monOpen+satClose+satOpen+sunClose+sunOpen+thrClose+thrOpen+tueClose+tueOpen+wedClose+wedOpen+__typename%7Dfragment+ImageAssetFragment+on+SanityImageAsset%7B_id+label+title+url+source%7Bid+url+__typename%7Dmetadata%7Blqip+palette%7Bdominant%7Bbackground+foreground+__typename%7D__typename%7D__typename%7D__typename%7D"
        )
        logger.info("Pulling Location %s..." % loc)
        r2 = session.get(lurl, headers=headers)
        website = "burgerking.ca"
        typ = "Restaurant"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "CA"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        for line2 in r2.iter_lines():
            if ',"name":"' in line2:
                name = line2.split(',"name":"')[1].split('"')[0]
                try:
                    add = (
                        line2.split('"address1":"')[1].split('"')[0]
                        + " "
                        + line2.split('"address2":"')[1].split('"')[0]
                    )
                except:
                    add = line2.split('"address1":"')[1].split('"')[0]
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"stateProvince":"')[1].split('"')[0]
                try:
                    phone = line2.split('"phoneNumber":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split(",")[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                line2 = line2.replace("23:59:59", "00:00:00")
                try:
                    hours = (
                        "Mon: "
                        + line2.split('"monOpen":"')[1].split(':00"')[0].split(" ")[1]
                        + "-"
                        + line2.split('"monClose":"')[1].split(':00"')[0].split(" ")[1]
                    )
                    hours = (
                        hours
                        + "; "
                        + "Tue: "
                        + line2.split('"tueOpen":"')[1].split(':00"')[0].split(" ")[1]
                        + "-"
                        + line2.split('"tueClose":"')[1].split(':00"')[0].split(" ")[1]
                    )
                    hours = (
                        hours
                        + "; "
                        + "Wed: "
                        + line2.split('"wedOpen":"')[1].split(':00"')[0].split(" ")[1]
                        + "-"
                        + line2.split('"wedClose":"')[1].split(':00"')[0].split(" ")[1]
                    )
                    hours = (
                        hours
                        + "; "
                        + "Thu: "
                        + line2.split('"thrOpen":"')[1].split(':00"')[0].split(" ")[1]
                        + "-"
                        + line2.split('"thrClose":"')[1].split(':00"')[0].split(" ")[1]
                    )
                    hours = (
                        hours
                        + "; "
                        + "Fri: "
                        + line2.split('"friOpen":"')[1].split(':00"')[0].split(" ")[1]
                        + "-"
                        + line2.split('"friClose":"')[1].split(':00"')[0].split(" ")[1]
                    )
                    hours = (
                        hours
                        + "; "
                        + "Sat: "
                        + line2.split('"satOpen":"')[1].split(':00"')[0].split(" ")[1]
                        + "-"
                        + line2.split('"satClose":"')[1].split(':00"')[0].split(" ")[1]
                    )
                    if '"sunOpen":"' in line2:
                        hours = (
                            hours
                            + "; "
                            + "Sun: "
                            + line2.split('"sunOpen":"')[1]
                            .split(':00"')[0]
                            .split(" ")[1]
                            + "-"
                            + line2.split('"sunClose":"')[1]
                            .split(':00"')[0]
                            .split(" ")[1]
                        )
                    else:
                        hours = hours + "; Sun: Closed"
                except:
                    hours = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                if city == "":
                    if "," in add:
                        city = add.split(",")[1].strip()
                    else:
                        city = "<MISSING>"
                if "." not in lat or "." not in lng:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                if "4967 Clifton Hill" in add:
                    hours = "Mon: Closed; Tue: Closed; Wed: Closed; Thu: Closed; Fri: 12:00 p.m. - 8:00 p.m.; Sat: 12:00 p.m. - 8:00 p.m.; Sun: 12:00 p.m. - 7:00 p.m."
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
