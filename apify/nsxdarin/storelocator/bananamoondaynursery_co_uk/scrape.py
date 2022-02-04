from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "referer": "https://www.bananamoondaynursery.co.uk/",
    "origin": "https://www.bananamoondaynursery.co.uk",
    "x-csrf-token": "YVQliYlQ2jRGqNaSmM3aIiLJpNSB7GS7RxIQ5oqa",
    "cookie": "_ga=GA1.3.753730042.1643906684; _gid=GA1.3.528204874.1643906684; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjSession_1235664=eyJpZCI6ImNhYmNlMzNlLWExNzAtNDE4Ny04MmM4LTBkOGQzNDQ4NzJjMCIsImNyZWF0ZWQiOjE2NDM5MDY2ODU0MjksImluU2FtcGxlIjp0cnVlfQ==; _hjAbsoluteSessionInProgress=0; _hjSessionUser_1235664=eyJpZCI6IjE4YTAyMmRkLWFjOGMtNTQzMy04ZDFhLTk1Njk1NWU1YzkwYyIsImNyZWF0ZWQiOjE2NDM5MDY2ODQ5MDYsImV4aXN0aW5nIjp0cnVlfQ==; XSRF-TOKEN=eyJpdiI6Im80NFNIdytYc1VPS1VOXC9ZMHFRbGJ3PT0iLCJ2YWx1ZSI6IlhRdHRoREFiXC9OZms0bEtJd0p2RnVaQTQxbFdvbVwvUXBadDRIb1kwTk1WcjNvYmVHNU1OSElIVDdmNCttbnprRCIsIm1hYyI6ImNiNjcyNWZkN2YzMzg2YzJhN2ZiMzMyYjliODQyYWQxZDg1Y2IxYTZiYmM5ZDExZDExNjZhZGFlMTQwNDRiZWIifQ%3D%3D; banana_moon_day_nursery_session=eyJpdiI6IkxKS1RRMVJBYkxYcEJ3UW5VT2NzUnc9PSIsInZhbHVlIjoibjBHTzdNK29ZdkQxb1Y2XC90YkJIZlJBaG1LNldURUNoNE5GeUxmU0dMb1BsOTVaNFhxZ01YeWpSVkt4MmJYNisiLCJtYWMiOiIzN2Q0MDBhM2ZkOTM0ZDY1N2NjM2M5ZDE1YmNkZGU1NDZkNzdhN2EzNWYxMTRjMTQ4MzMxNDAwMDg1ZWFlYzNmIn0%3D",
    "x-requested-with": "XMLHttpRequest",
    "x-xsrf-token": "eyJpdiI6Im80NFNIdytYc1VPS1VOXC9ZMHFRbGJ3PT0iLCJ2YWx1ZSI6IlhRdHRoREFiXC9OZms0bEtJd0p2RnVaQTQxbFdvbVwvUXBadDRIb1kwTk1WcjNvYmVHNU1OSElIVDdmNCttbnprRCIsIm1hYyI6ImNiNjcyNWZkN2YzMzg2YzJhN2ZiMzMyYjliODQyYWQxZDg1Y2IxYTZiYmM5ZDExZDExNjZhZGFlMTQwNDRiZWIifQ==",
}

logger = SgLogSetup().get_logger("bananamoondaynursery_co_uk")


def fetch_data():
    url = "https://www.bananamoondaynursery.co.uk/locations"
    payload = {
        "postcode": {
            "text": "",
            "icon": {"url": "/img/marker--secondary.png"},
            "position": {},
        }
    }
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "bananamoondaynursery.co.uk/"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["locations"]:
        name = item["name"]
        loc = "https://www.bananamoondaynursery.co.uk/find-us/" + item["slug"]
        lat = item["position"]["lat"]
        lng = item["position"]["lng"]
        add = item["address"]["line_1"]
        try:
            add = add + " " + item["address"]["line_2"]
        except:
            pass
        city = item["address"]["city"]
        state = "<MISSING>"
        zc = item["address"]["postcode"]
        phone = item["telephone"]
        hours = "Sun-Sat: " + item["start_time"] + "-" + item["end_time"]
        store = "<MISSING>"
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
