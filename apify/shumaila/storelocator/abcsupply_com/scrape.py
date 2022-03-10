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
    "path": "/wp-admin/admin-ajax.php?action=fetch_all_locations&_ajax_nonce=e9b967bfa9",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "visid_incap_2507554=jUC6BZVQSryokfX2vJNMwNxuJ2IAAAAAQUIPAAAAAACrtYVsiutTtumHKsiV658E; nlbi_2507554=FO/FczOL1y+cYAxHHQSnxAAAAADzDoHrb2JthtgcFIOrSozG; incap_ses_961_2507554=8MZCfBWpHwchBWGt9ihWDd5uJ2IAAAAAvt61f7MgfBEjvGte9I6Ovg==; _gcl_au=1.1.1632423397.1646751457; wp-wpml_current_language=en; _ga=GA1.2.481318390.1646751457; _gid=GA1.2.315332355.1646751457; _gat_UA-24726652-1=1; _fbp=fb.1.1646751457232.1823540262; reese84=3:vguabBU4gZMJxdxlGN20sA==:mEFQOfLsS2eDwzbU7zrrvIdJYoIlAbpXnMzu0zTBiyCJ8hJyAlsDRaisOTeC46kvCY3dR0X3r+ljCjaij4EqzCinEORWje86qjTsxdctIvsy2XlDkk84T0RFrpk28Dm5wXrtvIQfW0hb+boVcSzErxrmf5AyrGUm5K9TKDka1SFvzLQUJITRcFahnu3Yrwa5i3EeyfgIoLYm2NAksON2EAp2P9EbT5LH6S0DfwZIhgbIbMBiouLqcKheJEyQV0erge7nYGJ3E62tQNCIvBuaOBGoIVQNDr6+MInzLUE160oDVgsLw/vrjrlTFaXjv0fuffmvT0UpDuAjPYnjoVJbTKe/UUG7w8FBt520f4VZnjyolWP89/x1sU5jbsXhZiV/cA0HLZxxf2NkSB2qkl+dVMaMlTZ8rzEyVIMjk75qef26Z7LDkmu3Dl5NYRZxO5z6:QjQjX8X+Nf9caiiIsk/LhyqDszj30rCSie5UPIG6dAo=; _hjFirstSeen=1; _hjSession_1637281=eyJpZCI6IjllODEwZDQ3LWI5MDgtNGUzNC1hYjAxLTQ0ZGIwNDBlMzQ5MSIsImNyZWF0ZWQiOjE2NDY3NTE0NTc5NDUsImluU2FtcGxlIjp0cnVlfQ==; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; _hjSessionUser_1637281=eyJpZCI6IjFmYTIzMDQ3LWFmMTktNWIxNS1iZDBmLThmM2EwMmMxMzJjMiIsImNyZWF0ZWQiOjE2NDY3NTE0NTc5MjgsImV4aXN0aW5nIjp0cnVlfQ==; nlbi_2507554_2147483392=it1BeqoS/2VrZg1hHQSnxAAAAABhRgwM30jeRHE0607Ztm6U",
    "referer": "https://www.abcsupply.com/locations/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():
    os.environ["NO_PROXY"] = "abcsupply.com/"
    url = "https://www.abcsupply.com/wp-admin/admin-ajax.php?action=fetch_all_locations&_ajax_nonce=e9b967bfa9"
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
