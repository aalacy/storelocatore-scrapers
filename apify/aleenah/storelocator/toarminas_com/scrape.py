from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import usaddress
import re

logger = SgLogSetup().get_logger("toarminas_com")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here
    res = session.get("https://www.toarminas.com/locations/")
    soup = BeautifulSoup(res.text, "html.parser")
    state = (
        str(soup.find("script", {"id": "maplistko-js-extra"}))
        .split("var maplistScriptParamsKo =")[1]
        .split(";")[0]
    )
    jso = json.loads(state)
    jso = jso["KOObject"][0]["locations"]

    for js in jso:

        simple = js["simpledescription"].split("</p>\n<p>")
        phone = re.findall(r"(\(\d{3}\) \d{3}\-\d{4})", js["simpledescription"])[0]
        addr = (
            simple[0].replace("<br />\n", ",").replace("<p>", "").split("<strong>")[0]
        )  # .replace('<strong>','' ).replace('</p>','').replace('</strong>','' ).strip()

        tagged = usaddress.tag(addr)[0]

        street = tagged["AddressNumber"]
        if "StreetNamePreDirectional" in tagged:
            street += " " + tagged["StreetNamePreDirectional"]
        street += " " + tagged["StreetName"]
        if "StreetNamePostType" in tagged:
            street += " " + tagged["StreetNamePostType"]
        if "StateName" in tagged:
            state = tagged["StateName"]
        else:
            state = "<MISSING>"

        if "ZipCode" in tagged:
            zip = tagged["ZipCode"]
        else:
            zip = "<MISSING>"

        res = session.get(js["locationUrl"])
        soup = BeautifulSoup(res.text, "html.parser")
        if "Hour" in str(soup):
            hrs = str(soup.find("div", {"id": "MapDescription"})).replace("\n", "")
            tim = (
                re.findall("Hours(.*pm)", hrs)[0]
                .replace("<br/>", ", ")
                .strip(", ")
                .replace("</h3><ul><li>", "")
                .replace("</li><li>", ", ")
                .strip()
            )
        else:
            tim = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.toarminas.com",
            page_url=js["locationUrl"],
            location_name=js["title"],
            street_address=street,
            city=tagged["PlaceName"],
            state=state,
            zip_postal=zip,
            country_code="US",
            store_number=js["cssClass"].split("loc-")[1],
            phone=phone,
            location_type="<MISSING>",
            latitude=js["latitude"],
            longitude=js["longitude"],
            hours_of_operation=tim,
        )


def scrape():
    write_output(fetch_data())


scrape()
