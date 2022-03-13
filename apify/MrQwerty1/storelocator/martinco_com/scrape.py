from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser
from sgrequests import SgRequests
from sglogging import sglog

session = SgRequests(proxy_country="gb")

logger = sglog.SgLogSetup().get_logger(logger_name="martinco.com")


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING

    return street, city


def fetch_data(sgw: SgWriter):
    json_data = {
        "operationName": None,
        "variables": {
            "siteId": "2",
            "location": None,
            "limit": 300,
            "offset": 0,
        },
        "query": 'query ($siteId: [QueryArgument]!, $location: String, $limit: Int, $offset: Int) {\n  branches(siteId: $siteId, location: $location, limit: $limit, offset: $offset) {\n    id\n    ... on branch_branch_Entry {\n      url\n      uri\n      slug\n      title\n      latitude\n      longitude\n      distance\n      parent {\n        id\n        title\n        __typename\n      }\n      spoke\n      branchCard {\n        ... on branchCard_BlockType {\n          id\n          heroImage {\n            title\n            url\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      branchHero {\n        ... on branchHero_BlockType {\n          id\n          button {\n            ... on button_button_BlockType {\n              id\n              buttonText\n              buttonLink\n              __typename\n            }\n            __typename\n          }\n          heroImage {\n            title\n            url\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      branchInfo {\n        ... on branchInfo_BlockType {\n          id\n          email\n          address\n          city\n          telephone\n          reportARepair {\n            ... on reportARepair_button_BlockType {\n              id\n              buttonText\n              buttonLink\n              __typename\n            }\n            __typename\n          }\n          openingHours {\n            monday\n            tuesday\n            wednesday\n            thursday\n            friday\n            saturday\n            __typename\n          }\n          socials {\n            ... on socials_channel_BlockType {\n              id\n              channelType\n              channelUrl\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  branchCount\n  seomatic(uri: "estate-agents-and-letting-agents", asArray: true) {\n    metaTitleContainer\n    metaLinkContainer\n    metaScriptContainer\n    metaJsonLdContainer\n    metaTagContainer\n    __typename\n  }\n}\n',
    }

    r = session.post("https://cms.martinco.com/api", headers=headers, json=json_data)
    logger.info(f"Response: {r}")
    js = r.json()["data"]["branches"]
    for j in js:
        page_url = j.get("url")
        store_number = j.get("id")
        location_name = j.get("title")
        b = j["branchInfo"][0]

        _tmp = []
        try:
            hours = b["openingHours"][0]
        except:
            hours = dict()
        for day, inter in hours.items():
            if "_" not in day:
                _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

        source = b.get("address") or ""
        tree = html.fromstring(source)
        address = tree.xpath("//text()")
        address = list(filter(None, [raw.strip() for raw in address]))
        raw_address = ", ".join(address)
        postal = address.pop()
        street_address, city = get_international(", ".join(address))
        phone = b.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="GB",
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    logger.info("Started Crawling")
    locator_domain = "martinco.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
