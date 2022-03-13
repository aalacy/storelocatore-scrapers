from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import os

session = SgRequests()
headers = {
    "authority": "www.abcsupply.com",
    "method": "GET",
    "path": "/wp-admin/admin-ajax.php?action=fetch_all_locations&_ajax_nonce=1bd2076898",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "_gcl_au=1.1.1632423397.1646751457; _ga=GA1.2.481318390.1646751457; _fbp=fb.1.1646751457232.1823540262; _hjSessionUser_1637281=eyJpZCI6IjFmYTIzMDQ3LWFmMTktNWIxNS1iZDBmLThmM2EwMmMxMzJjMiIsImNyZWF0ZWQiOjE2NDY3NTE0NTc5MjgsImV4aXN0aW5nIjp0cnVlfQ==; nlbi_2507554=Uieod477VXgo2/UQHQSnxAAAAACfUfjTMMFZVc8EuoUfd2tK; incap_ses_217_2507554=8+S4QbIT6UiKnh4X6vACA+7zLWIAAAAAi0iq2ikKFVe0U8Dzy9OPUw==; reese84=3:zcRSr7f8gK2gKpxhH4S0zg==:YgeetTz/jwqkF/B3j06UHpSfrTVdYxZiONBrQPoo8wa3jJkywXl7wdKYjXVXYB02uxA2aBjmTbOOvEPwImdhCEcxsgD1FHGLHg67PsDgxey4m2PlSm0WM9X1+Vu8ITZwizRsFUVXUbDIz1wuV5HXT8U/QNMu3mrbSTLRPNeZDkBwoVKHX+O2OVANlE7+yI3hIcsObKKgcezMsFMqdre+8IzFmBwWz5oBqtUUosjHsoXa5k2csx7wLRnKO+Yd/VUZMZWKrsatfq3tJtNX1fEgGxOovgnUqs5t+Mlxfwnk26gYdaqMRTNi4ruwdoVCzKV4jupswjMPg2/oLrTuHTtonrqsK5/6fRDt8bfhp/CPGmOoj7rzJbdg5Y7iIzh3UI2xQOw/7fOVhyAxth/RsuBwkDU9PbJetufw0eLiUhOWPQDXjVXNbJ9PhG18Jo9qOLKf:Q+WL80medoTKWx2CfQj2axXVT9jTZwHZApim2tt7k9g=; incap_ses_1564_2507554=82qhD7dhdFAPMe9Uu3G0FRP0LWIAAAAApCHS8T/70DG5pGUXPqhqJw==; incap_sh_2507554=GfQtYgAAAAD5ItJ+DAAImei3kQYQk+i3kQbgA+AnD5NKCVLeRKFihpte; visid_incap_2507554=jUC6BZVQSryokfX2vJNMwNxuJ2IAAAAAQkIPAAAAAACAM+aiASchi9hkvLchYjNEDm4vKBaCJ/pw; wp-wpml_current_language=en; _gid=GA1.2.1124066357.1647178783; _gat_UA-24726652-1=1; _hjIncludedInPageviewSample=1; _hjSession_1637281=eyJpZCI6IjViNjQxNTcwLTUwZTQtNDBmYi05NTQ0LTMxOGNlY2NlMmQxOCIsImNyZWF0ZWQiOjE2NDcxNzg3ODM4NzUsImluU2FtcGxlIjp0cnVlfQ==; _hjAbsoluteSessionInProgress=0; nlbi_2507554_2147483392=pDHqJAp4h1CtvCJsHQSnxAAAAADzwgHk8sF8iOWmSxX+MD8Y",
    "referer": "https://www.abcsupply.com/locations/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():
    os.environ["NO_PROXY"] = "abcsupply.com/"
    url = "https://www.abcsupply.com/wp-admin/admin-ajax.php?action=fetch_all_locations&_ajax_nonce=1bd2076898"
    session.trust_env = False

    divlist = session.get(url, headers=headers).json()
    for div in divlist:
        loclist = div["locations"]
        for loc in loclist:

            store = loc["branchNumber"]
            street = loc["address1"] + str(loc["address2"])
            street = street.replace("None", "")
            city = loc["city"]
            state = loc["state"]
            pcode = loc["postalCode"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            try:
                phone = loc["phoneNumber"].strip()
            except:
                phone = "<MISSING>"
            try:
                hourslist = loc["seasonalHours"][0]["hourDetails"][0]
                hours = (
                    hourslist["hoursText"]
                    + " "
                    + hourslist["openTime"]
                    + " - "
                    + hourslist["closeTime"]
                )
            except:
                hours = "<MISSING>"
            link = "https://www.abcsupply.com/locations/location/?id=" + str(store)
            title = "ABC Supply - " + city + ", " + state
            yield SgRecord(
                locator_domain="https://www.abcsupply.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(store),
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
