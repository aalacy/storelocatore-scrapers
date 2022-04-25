from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time
import json

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Algolia-API-Key": "8cf40864df513111d39148923f754024",
    "X-Algolia-Application-Id": "6OBGA4VJKI",
}

logger = SgLogSetup().get_logger("tagheuer_com")


def fetch_data():
    countries = [
        "ad",
        "ag",
        "am",
        "ao",
        "aw",
        "az",
        "ba",
        "bb",
        "bd",
        "bg",
        "bh",
        "bi",
        "bl",
        "bm",
        "bn",
        "bo",
        "bs",
        "by",
        "bz",
        "ci",
        "cl",
        "cr",
        "cw",
        "cy",
        "do",
        "ec",
        "ee",
        "eg",
        "et",
        "fj",
        "gd",
        "ge",
        "gg",
        "gi",
        "gp",
        "gt",
        "gu",
        "hn",
        "hu",
        "ie",
        "im",
        "iq",
        "is",
        "je",
        "jm",
        "jo",
        "kh",
        "kn",
        "kw",
        "ky",
        "kz",
        "lb",
        "lc",
        "li",
        "lk",
        "lu",
        "lv",
        "ma",
        "mf",
        "mg",
        "mk",
        "mn",
        "mo",
        "mp",
        "mq",
        "mt",
        "mu",
        "mv",
        "mz",
        "nc",
        "ng",
        "np",
        "nz",
        "om",
        "pa",
        "pe",
        "ph",
        "pk",
        "pr",
        "py",
        "qa",
        "re",
        "ro",
        "rs",
        "sc",
        "si",
        "sk",
        "sm",
        "sv",
        "sx",
        "tc",
        "th",
        "tn",
        "ua",
        "uy",
        "uz",
        "ve",
        "vg",
        "vi",
        "ye",
        "ae",
        "al",
        "ar",
        "at",
        "au",
        "be",
        "br",
        "ca",
        "ch",
        "cn",
        "co",
        "cz",
        "de",
        "dk",
        "dz",
        "es",
        "fi",
        "fr",
        "gb",
        "gr",
        "hk",
        "hr",
        "id",
        "il",
        "in",
        "it",
        "jp",
        "kr",
        "mx",
        "my",
        "nl",
        "no",
        "pl",
        "pt",
        "ru",
        "sa",
        "se",
        "sg",
        "tr",
        "tw",
        "us",
        "za",
    ]

    for cc in countries:
        session = SgRequests()
        time.sleep(3)
        url = "https://6obga4vjki-dsn.algolia.net/1/indexes/stores/query"
        payload = {
            "params": "filters=country:"
            + cc
            + "&attributesToRetrieve=address,Latitude,zip,country,phone,type,id,image,address2,email,name,description,services,payments,city,openingHours,exceptionalHours,contactUsForm,_geoloc,i18nAddress,specialProducts,image1,image2,image3,timezone,sfccUrl,getRankingInfo:1",
            "aroundRadius": "15000",
            "hitsPerPage": "1000",
            "getRankingInfo": "1",
            "attributesToRetrieve": "address,Latitude,zip,country,phone,type,id,image,address2,email,name,description,services,payments,city,openingHours,exceptionalHours,contactUsForm,_geoloc,i18nAddress,specialProducts,image1,image2,image3,timezone,sfccUrl",
            "attributesToHighlight": "name",
        }
        r = session.post(url, headers=headers, data=json.dumps(payload))
        website = "tagheuer.com"
        country = cc.upper()
        logger.info("Pulling %s..." % cc)
        for item in json.loads(r.content)["hits"]:
            add = item["address"]
            name = item["name"]
            zc = item["zip"]
            city = item["city"]
            phone = item["phone"]
            state = "<MISSING>"
            typ = item["type"]
            loc = "https://www.tagheuer.com/us/en/" + item["sfccUrl"]
            hrstring = str(item["openingHours"])
            try:
                hours = (
                    "Sunday: "
                    + hrstring.split("'0'")[1].split("'start': '")[1].split("'")[0]
                    + "-"
                    + hrstring.split("'0'")[1].split("'end': '")[1].split("'")[0]
                )
                hours = (
                    hours
                    + "; Monday: "
                    + hrstring.split("'1'")[1].split("'start': '")[1].split("'")[0]
                    + "-"
                    + hrstring.split("'1'")[1].split("'end': '")[1].split("'")[0]
                )
                hours = (
                    hours
                    + "; Tuesday: "
                    + hrstring.split("'2'")[1].split("'start': '")[1].split("'")[0]
                    + "-"
                    + hrstring.split("'2'")[1].split("'end': '")[1].split("'")[0]
                )
                hours = (
                    hours
                    + "; Wednesday: "
                    + hrstring.split("'3'")[1].split("'start': '")[1].split("'")[0]
                    + "-"
                    + hrstring.split("'3'")[1].split("'end': '")[1].split("'")[0]
                )
                hours = (
                    hours
                    + "; Thursday: "
                    + hrstring.split("'4'")[1].split("'start': '")[1].split("'")[0]
                    + "-"
                    + hrstring.split("'4'")[1].split("'end': '")[1].split("'")[0]
                )
                hours = (
                    hours
                    + "; Friday: "
                    + hrstring.split("'5'")[1].split("'start': '")[1].split("'")[0]
                    + "-"
                    + hrstring.split("'5'")[1].split("'end': '")[1].split("'")[0]
                )
                hours = (
                    hours
                    + "; Saturday: "
                    + hrstring.split("'6'")[1].split("'start': '")[1].split("'")[0]
                    + "-"
                    + hrstring.split("'6'")[1].split("'end': '")[1].split("'")[0]
                )
            except:
                hours = "<MISSING>"
            lat = item["_geoloc"]["lat"]
            lng = item["_geoloc"]["lng"]
            store = item["objectID"]
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
