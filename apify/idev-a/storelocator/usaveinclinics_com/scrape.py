from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import json


locator_domain = "https://www.usaveinclinics.com"


def fetch_data():
    with SgRequests() as session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "cookie": "__smVID=12b7023c367b6aa1cc3d61d1f5ab061f65f57eb8e3934ee7a94bb45eb153eff7; __cfduid=d4e8edcbf62d0ca44be7a34d85ae6d4ea1614154793; pll_language=en; _gcl_au=1.1.332345539.1614154798; apexchat_dropdown_invitation=_max; livechat_agent_alias_id=6195; livechat_profile_id=224681; _ga=GA1.2.1507809367.1614154800; _gid=GA1.2.384462527.1614154800; calltrk_referrer=direct; calltrk_landing=https%3A//www.usaveinclinics.com/; apexchat_dompopup_chatwindow=_rendered; PHPSESSID=dslbk9bs578nm65qdg6fbe6ahr; livechat_original_referrer=https%253A%252F%252Fwww.usaveinclinics.com%252F; livechat_visitor_id=917900193; __smToken=Bm4PxIZAUxsdDFb9fEsjeNSh; __hstc=109396570.0a7c061a62a8ed3ef1ba85d825b2a634.1614154817050.1614154817050.1614154817050.1; hubspotutk=0a7c061a62a8ed3ef1ba85d825b2a634; __hssrc=1; livechat_prechat_started=false; livechat_v3_invitation_shown=true; livechat_is_page_refreshed=false; livechat_operator_id=undefined; livechat_prechat_lastmessage=%7B%22index%22%3A0%2C%22duration%22%3A3000%7D; apexchat_prechat_invitation=_max; __hssc=109396570.3.1614154817051; livechat_prechat_messagecounter=1; livechat_prechat_message_ids=%5B89318637%5D",
            "referer": "https://www.usaveinclinics.com/",
            "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        }
        res = session.get("https://www.usaveinclinics.com/locations", headers=headers)
        stores = bs(res.text, "lxml").select("section.location-listing")
        for store in stores:
            page_url = store.select_one("a")["href"]
            location_name = store.select_one("a").text
            if "Coming Soon" in location_name:
                continue
            address = store.select_one("div.location-listing__info-item").contents
            address = [x.string for x in address if x.string is not None]
            address = [x.replace("\n", "") for x in address if x != "\n"]
            address = " ".join(address[1:])
            address = parse_address_intl(address)
            zip = address.postcode
            state = address.state
            city = address.city
            street_address = (
                address.street_address_1
                + " "
                + (
                    address.street_address_2
                    if address.street_address_2 is not None
                    else ""
                )
            )
            res = session.get(page_url, headers=headers)
            detail = json.loads(
                res.text.split('<script type="application/ld+json">')[1].split(
                    "</script>"
                )[0]
            )
            latitude = detail["geo"]["latitude"]
            longitude = detail["geo"]["longitude"]
            phone = detail["telephone"]
            location_type = detail["@type"]
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=zip,
                state=state,
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                location_type=location_type,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
