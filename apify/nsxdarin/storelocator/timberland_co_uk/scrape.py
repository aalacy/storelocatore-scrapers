from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("timberland_co_uk")


def fetch_data():
    url = "https://hosted.where2getit.com/timberland/timberlandeu/rest/locatorsearch?like=0.9297644562205771&lang=en_US"
    payload = {
        "request": {
            "appkey": "2047B914-DD9C-3B95-87F3-7B461F779AEB",
            "formdata": {
                "geoip": False,
                "dataview": "store_default",
                "atleast": 1,
                "limit": 250,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "Liverpool",
                            "country": "UK",
                            "latitude": 53.4083714,
                            "longitude": -2.9915726,
                            "state": "",
                            "province": "Merseyside",
                            "city": "Liverpool",
                            "address1": "",
                            "postalcode": "",
                        }
                    ]
                },
                "searchradius": "1000",
                "radiusuom": "km",
                "order": "retail_store,outletstore,authorized_reseller,_distance",
                "where": {
                    "or": {
                        "retail_store": {"eq": ""},
                        "outletstore": {"eq": ""},
                        "icon": {"eq": ""},
                    },
                    "and": {
                        "service_giftcard": {"eq": ""},
                        "service_clickcollect": {"eq": ""},
                        "service_secondchance": {"eq": ""},
                        "service_appointment": {"eq": ""},
                        "service_reserve": {"eq": ""},
                        "service_onlinereturns": {"eq": ""},
                        "service_orderpickup": {"eq": ""},
                        "service_virtualqueuing": {"eq": ""},
                        "service_socialpage": {"eq": ""},
                        "service_eventbrite": {"eq": ""},
                        "service_storeevents": {"eq": ""},
                        "service_whatsapp": {"eq": ""},
                    },
                },
                "false": "0",
            },
        }
    }

    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "timberland.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["response"]["collection"]:
        phone = item["phone"]
        store = "<MISSING>"
        add = str(item["address1"])
        if item["address2"] is not None:
            add = add + " " + str(item["address2"])
        if item["address3"] is not None:
            add = add + " " + str(item["address3"])
        add = add.strip()
        city = item["city"]
        state = item["province"]
        zc = item["postalcode"]
        lat = item["latitude"]
        lng = item["longitude"]
        name = item["name"]
        cty = item["country"]
        name = name.replace("&reg;", "").replace("  ", " ").replace("  ", " ")
        hours = "<MISSING>"
        if state == "" or state is None:
            state = "<MISSING>"
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if cty == "UK":
            if "Outlet" in name:
                typ = "Timberland Outlet Store"
            else:
                typ = "Timberland Store"
            if "TBC" in phone:
                phone = "<MISSING>"
            add = add.replace("None", "").strip()
            phone = phone.replace("Tel:", "").strip()
            name = name.replace("<br>", "")
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

    url = "https://hosted.where2getit.com/timberland/timberlandeu/rest/locatorsearch?like=0.9297644562205771&lang=en_US"
    payload = {
        "request": {
            "appkey": "2047B914-DD9C-3B95-87F3-7B461F779AEB",
            "formdata": {
                "geoip": False,
                "dataview": "store_default",
                "atleast": 1,
                "limit": 250,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "RM20",
                            "country": "UK",
                            "latitude": 51.4778987,
                            "longitude": 0.2760807,
                            "state": "",
                            "province": "Thurrock",
                            "city": "",
                            "address1": "",
                            "postalcode": "RM20",
                        }
                    ]
                },
                "searchradius": "250",
                "radiusuom": "km",
                "order": "retail_store,outletstore,authorized_reseller,_distance",
                "where": {
                    "or": {
                        "retail_store": {"eq": ""},
                        "outletstore": {"eq": ""},
                        "icon": {"eq": ""},
                    },
                    "and": {
                        "service_giftcard": {"eq": ""},
                        "service_clickcollect": {"eq": ""},
                        "service_secondchance": {"eq": ""},
                        "service_appointment": {"eq": ""},
                        "service_reserve": {"eq": ""},
                        "service_onlinereturns": {"eq": ""},
                        "service_orderpickup": {"eq": ""},
                        "service_virtualqueuing": {"eq": ""},
                        "service_socialpage": {"eq": ""},
                        "service_eventbrite": {"eq": ""},
                        "service_storeevents": {"eq": ""},
                        "service_whatsapp": {"eq": ""},
                    },
                },
                "false": "0",
            },
        }
    }

    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "timberland.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    add = "332 Upper Level 114 West Thurrock Way"
    city = "Grays"
    zc = "RM20 2ZP"
    state = "<MISSING>"
    store = "<MISSING>"
    loc = "<MISSING>"
    name = "TIMBERLAND - LAKESIDE"
    phone = "01708 862692"
    lat = "51.489"
    lng = "0.2836034"
    hours = "<MISSING>"
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
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["response"]["collection"]:
        phone = item["phone"]
        store = "<MISSING>"
        add = str(item["address1"])
        if item["address2"] is not None:
            add = add + " " + str(item["address2"])
        if item["address3"] is not None:
            add = add + " " + str(item["address3"])
        add = add.strip()
        city = item["city"]
        state = item["province"]
        zc = item["postalcode"]
        lat = item["latitude"]
        lng = item["longitude"]
        name = item["name"]
        cty = item["country"]
        name = name.replace("&reg;", "").replace("  ", " ").replace("  ", " ")
        hours = "<MISSING>"
        if state == "" or state is None:
            state = "<MISSING>"
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if cty == "UK":
            if "Outlet" in name:
                typ = "Timberland Outlet Store"
            else:
                typ = "Timberland Store"
            if "TBC" in phone:
                phone = "<MISSING>"
            add = add.replace("None", "").strip()
            phone = phone.replace("Tel:", "").strip()
            name = name.replace("<br>", "")
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
