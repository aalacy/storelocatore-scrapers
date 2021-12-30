from sgrequests import SgRequests
import usaddress
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def fetch_data():
    url = "https://www.getezmoney.com/find-a-location/"
    payload = {"zip_code": 10002, "distance": 10000, "referral_search": "GO"}
    r = session.post(url, headers=headers, data=payload)
    for line in r.iter_lines():
        if 'valign="top">Website</td>' in line:
            items = line.split('valign="top">Website</td>')
            for item in items:
                if '<div id="content">' not in item:
                    loc = item.split('valign="top"><a href="')[1].split('"')[0]
                    website = "getezmoney.com"
                    name = item.split('<a href="')[1].split('">')[1].split("<")[0]
                    city = (
                        item.split('href="')[1]
                        .split(">")[1]
                        .split("<")[0]
                        .split(",")[0]
                    )
                    state = (
                        item.split('href="')[1]
                        .split(">")[1]
                        .split(",")[1]
                        .split("<")[0]
                        .strip()
                    )
                    try:
                        rawadd = item.split(
                            '>Address</td><td class="referral-value" valign="top">'
                        )[1].split("<")[0]
                    except:
                        rawadd = ""
                    phone = item.split('<a href="tel:')[1].split('"')[0]
                    country = "US"
                    typ = "Location"
                    try:
                        add = usaddress.tag(rawadd)
                        baseadd = add[0]
                        if "AddressNumber" not in baseadd:
                            baseadd["AddressNumber"] = ""
                        if "StreetName" not in baseadd:
                            baseadd["StreetName"] = ""
                        if "StreetNamePostType" not in baseadd:
                            baseadd["StreetNamePostType"] = ""
                        if "PlaceName" not in baseadd:
                            baseadd["PlaceName"] = "<INACCESSIBLE>"
                        if "StateName" not in baseadd:
                            baseadd["StateName"] = "<INACCESSIBLE>"
                        if "ZipCode" not in baseadd:
                            baseadd["ZipCode"] = "<INACCESSIBLE>"
                        address = (
                            add[0]["AddressNumber"]
                            + " "
                            + add[0]["StreetName"]
                            + " "
                            + add[0]["StreetNamePostType"]
                        )
                        address = address.encode("ascii").decode()
                        if address == "":
                            address = "<INACCESSIBLE>"
                        zc = add[0]["ZipCode"]
                    except:
                        pass

                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    store = "<MISSING>"
                    address = address.strip().replace("\t", "")
                    hours = "Mon: " + item.split("<td>Monday</td><td>")[1].split(
                        "</tr>"
                    )[0].replace("</td><td>", "-").replace("</td>", "")
                    hours = (
                        hours
                        + "; Tue: "
                        + item.split("<td>Tuesday</td><td>")[1]
                        .split("</tr>")[0]
                        .replace("</td><td>", "-")
                        .replace("</td>", "")
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + item.split("<td>Wednesday</td><td>")[1]
                        .split("</tr>")[0]
                        .replace("</td><td>", "-")
                        .replace("</td>", "")
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + item.split("<td>Thursday</td><td>")[1]
                        .split("</tr>")[0]
                        .replace("</td><td>", "-")
                        .replace("</td>", "")
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + item.split("<td>Friday</td><td>")[1]
                        .split("</tr>")[0]
                        .replace("</td><td>", "-")
                        .replace("</td>", "")
                    )
                    hours = (
                        hours
                        + "; Sat: "
                        + item.split("<td>Saturday</td><td>")[1]
                        .split("</tr>")[0]
                        .replace("</td><td>", "-")
                        .replace("</td>", "")
                    )
                    hours = (
                        hours
                        + "; Sun: "
                        + item.split("<td>Sunday</td><td>")[1]
                        .split("</tr>")[0]
                        .replace("</td><td>", "-")
                        .replace("</td>", "")
                    )
                    if address == "":
                        address = "<MISSING>"
                    if rawadd == "":
                        rawadd = "<MISSING>"
                    yield SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        raw_address=rawadd,
                        street_address=address,
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
