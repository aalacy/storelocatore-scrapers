from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("outdoorvoices")

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.outdoorvoices.com",
    "referer": "https://www.outdoorvoices.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def payload1(shopifyId):
    return {
        "query": "fragment image on ImageNode {\n  id\n  alt\n  height\n  src\n  width\n}\n\nquery GetShop($shopifyId: String!) {\n  shop(shopifyId: $shopifyId) {\n    city\n    description\n    email\n    hours {\n      edges {\n        node {\n          id\n          label\n          times\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    id\n    images: shopImages {\n      edges {\n        node {\n          group\n          id\n          image {\n            ...image\n            __typename\n          }\n          landscape\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    phoneNumber\n    state\n    streetAddress\n    tagline\n    title\n    zipCode\n    __typename\n  }\n}\n",
        "operationName": "GetShop",
        "variables": {"shopifyId": shopifyId},
    }


def payload():
    return {
        "query": "fragment image on ImageNode {\n  id\n  alt\n  height\n  src\n  width\n}\n\nquery GetShops {\n  shops {\n    edges {\n      node {\n        id\n        title: titleList\n        city\n        comingSoon\n        state\n        url: shopifyPageUrl\n        image {\n          ...image\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        "operationName": "GetShops",
        "variables": {},
    }


def fetch_data():
    locator_domain = "https://www.outdoorvoices.com/"
    base_url = "https://api.dointhings.com/graphql"
    with SgRequests() as session:
        links = session.post(base_url, headers=_headers, json=payload()).json()["data"][
            "shops"
        ]["edges"]
        logger.info(f"{len(links)} found")
        for link in links:
            if link["node"]["comingSoon"]:
                continue
            page_url = link["node"]["url"]
            logger.info(page_url)
            res = session.get(page_url, headers=headers).text
            shopifyId = (
                res.split("window.OV.PAGE_ID =")[1].split("</script>")[0].strip()[:-1]
            )
            _ = session.post(
                base_url, headers=_headers, json=payload1(shopifyId)
            ).json()["data"]["shop"]
            hours = []
            for hh in _["hours"]["edges"]:
                hours.append(f"{hh['node']['label']}: {hh['node']['times']}")
            yield SgRecord(
                page_url=page_url,
                store_number=shopifyId,
                location_name=_["title"],
                street_address=_["streetAddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipCode"],
                country_code="US",
                phone=_["phoneNumber"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
