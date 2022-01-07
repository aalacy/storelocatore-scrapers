from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.hooters.com/api/search_locations.json?latitude=40&longitude=-90"
    r = session.get(url, headers=headers)
    website = "hooters.com"
    typ = "<MISSING>"
    for item in json.loads(r.content)["locations"]:
        store = item["id"]
        name = item["name"]
        phone = item["phone"]
        zc = item["zip"]
        add = item["address"]["line-1"]
        csz = item["address"]["line-2"]
        try:
            city = csz.split(",")[0].strip()
        except:
            city = "<MISSING>"
        try:
            state = csz.split(",")[1].strip().split(" ")[0]
        except:
            state = "<MISSING>"
        if "Mexico" in csz:
            country = "MX"
        else:
            country = "US"
        if "Canada" in csz:
            country = "CA"
        if "Thailand" in csz:
            country = "TH"
        if "Brazil" in csz:
            country = "BR"
        if "Costa Rica" in csz:
            country = "CR"
        if "South Africa" in csz:
            country = "ZA"
        if "China" in csz:
            country = "CN"
        if "Japan" in csz:
            country = "JP"
        if "Germany" in csz:
            country = "DE"
        if "United Kingdom" in csz:
            country = "GB"
        if "Czech" in csz:
            country = "CZ"
        if "Switzerland" in csz:
            country = "CH"
        if " 0" in city:
            city = city.split(" 0")[0].strip()
        if " 1" in city:
            city = city.split(" 1")[0].strip()
        if " 2" in city:
            city = city.split(" 2")[0].strip()
        if " 3" in city:
            city = city.split(" 3")[0].strip()
        if " 4" in city:
            city = city.split(" 4")[0].strip()
        if " 5" in city:
            city = city.split(" 5")[0].strip()
        if " 6" in city:
            city = city.split(" 6")[0].strip()
        if " 7" in city:
            city = city.split(" 7")[0].strip()
        if " 8" in city:
            city = city.split(" 8")[0].strip()
        if " 9" in city:
            city = city.split(" 9")[0].strip()
        if "Beijing" in state:
            state = "<MISSING>"
            country = "CN"
        if " China" in city:
            city = city.split(" China")[0]
        if " Costa Rica" in city:
            city = city.split(" Costa")[0]
        if " Brazil" in city:
            city = city.split(" Brazil")[0]
        if " Japan" in city:
            city = city.split(" Japan")[0]
        if " South Africa" in city:
            city = city.split(" South Africa")[0]
        if " Australia" in city:
            city = city.split(" Australia")[0]
            country = "AU"
        lat = item["latitude"]
        lng = item["longitude"]
        if "Cozumel" in city:
            city = "Cozumel"
        if "Medellin" in city:
            country = "CO"
            city = "Medellin"
        if "Nassau Bahamas" in city:
            country = "BS"
            city = "Nassau"
        if "Dominican Republic" in city:
            city = city.split("Dominican Republic")[0].strip()
            country = "DR"
        if "Switzerland" in city:
            city = city.split(" Switzerland")[0].strip()
        if "Guatemala Guatemala" in city:
            city = "Guatemala"
            country = "GT"
        if "Czech Republic" in city:
            city = city.split("Czech Republic")[0].strip()
        loc = "https://hooters.com" + item["detailsUrl"].replace("\\", "")
        try:
            hours = (
                "Mon: "
                + item["hours"]["mon"]["open"].rsplit(":", 1)[0]
                + "-"
                + item["hours"]["mon"]["close"].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Tue: "
                + item["hours"]["tue"]["open"].rsplit(":", 1)[0]
                + "-"
                + item["hours"]["tue"]["close"].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Wed: "
                + item["hours"]["wed"]["open"].rsplit(":", 1)[0]
                + "-"
                + item["hours"]["wed"]["close"].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Thu: "
                + item["hours"]["thu"]["open"].rsplit(":", 1)[0]
                + "-"
                + item["hours"]["thu"]["close"].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Fri: "
                + item["hours"]["fri"]["open"].rsplit(":", 1)[0]
                + "-"
                + item["hours"]["fri"]["close"].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Sat: "
                + item["hours"]["sat"]["open"].rsplit(":", 1)[0]
                + "-"
                + item["hours"]["sat"]["close"].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; Sun: "
                + item["hours"]["sun"]["open"].rsplit(":", 1)[0]
                + "-"
                + item["hours"]["sun"]["close"].rsplit(":", 1)[0]
            )
        except:
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


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
