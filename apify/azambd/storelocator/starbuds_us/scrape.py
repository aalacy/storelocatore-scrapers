import json
import time
from lxml import html

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog


MISSING = "<MISSING>"
website = "https://www.starbuds.us"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetchNodeText(node):
    results = []
    for i, text_line in enumerate(node):
        span_text = [x.strip() for x in text_line.xpath(".//text()")]
        results.append(span_text)
    return results


def getFeatureData(url):
    response = session.get(url)
    body = html.fromstring(response.text, "lxml")
    featuredJsonLink = body.xpath(
        '//link[contains(@id, "features_") and @id != "features_masterPage"]/@href'
    )[0]
    response = session.get(featuredJsonLink)
    return {"data": json.loads(response.text), "body": body}


def fetchLocationStores(url):
    compProps = getFeatureData(url)["data"]["props"]["render"]["compProps"]
    storeLinks = []
    for key in compProps.keys():
        if (
            "label" in compProps[key]
            and compProps[key]["label"] == "VIEW HOURS, SPECIALS AND MENU"
        ):
            storeLinks.append(compProps[key]["link"]["href"])
    return storeLinks


def fetchStoreLinks():
    compProps = getFeatureData(website + "/locations")["data"]["props"]["render"][
        "compProps"
    ]
    storeLinks = []
    for key in compProps.keys():
        if "skin" in compProps[key] and compProps[key]["skin"] == "BasicButton":
            url = compProps[key]["link"]["href"]
            if "LOCATIONS" in compProps[key]["label"]:
                for link in fetchLocationStores(url):
                    if link not in storeLinks:
                        storeLinks.append(link)
            elif url not in storeLinks:
                storeLinks.append(url)
    storeLinks.sort()
    return storeLinks


def fetchStoreDetails(link):
    featuredData = getFeatureData(link)
    body = featuredData["body"]
    data = featuredData["data"]

    title = (
        (" ".join(body.xpath("//h1/span/span/text()")))
        .replace("Coming Soon!", "")
        .replace("&nbsp;", " ")
        .strip()
    )

    phone = body.xpath('//a[contains(@href, "tel:")]/span/span/text()')
    if len(phone) == 0:
        phone = body.xpath('//a[contains(@href, "tel:")]/span/text()')
        if len(phone) == 0:
            phone = body.xpath(
                '//span[contains(text(), "(") and contains(text(), ")")]/text()'
            )
            if len(phone) == 0:
                phone = [MISSING]

    phone = phone[0].replace("tel:", "").strip()

    operations = []
    hoursP = body.xpath("//span[text()='HOURS']")
    for hourP in hoursP:
        parentDiv = hourP.getparent().getparent().getparent().getparent()
        dayParts = fetchNodeText(parentDiv)
        for dayPart in dayParts[1:]:
            operations.append("".join(dayPart))
    if len(operations) == 0:
        phone = MISSING

    location = {}

    compProps = data["props"]["render"]["compProps"]
    for key in compProps.keys():
        if "mapData" in compProps[key]:
            location = compProps[key]["mapData"]["locations"][0]
    store_number = data["props"]["seo"]["pageId"]
    return {
        "title": title,
        "phone": phone,
        "operations": ", ".join(operations),
        "location": location,
        "store_number": store_number,
    }


def fetchData():
    storeLinks = fetchStoreLinks()
    log.debug(f"Total store count={len(storeLinks)}")

    for link in storeLinks:
        log.info(f"Scrapping {link} ...")
        details = fetchStoreDetails(link)
        title = details["title"]
        phone = details["phone"]
        operations = details["operations"]
        store_number = details["store_number"]
        location = details["location"]

        locationParts = location["address"].split(", ")
        if " " not in locationParts[2]:
            locationParts[2] = locationParts[2] + " " + MISSING
        country_code = "US"
        if locationParts[3] != "USA":
            continue

        city = locationParts[1]
        state = locationParts[2].split(" ")[0]
        zip_postal = str(locationParts[2].split(" ")[1])
        street_address = locationParts[0]
        yield SgRecord(
            locator_domain=website,
            page_url=link,
            location_name=title,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=str(location["latitude"]),
            longitude=str(location["longitude"]),
            hours_of_operation=operations,
        )


def scrape():
    start = time.time()
    results = fetchData()
    with SgWriter() as writer:
        for rec in results:
            writer.write_row(rec)

    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
