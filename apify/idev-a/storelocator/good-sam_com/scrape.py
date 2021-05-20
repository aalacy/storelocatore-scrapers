from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("good-sam")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.good-sam.com/"
        base_url = "https://www.good-sam.com/coveo/rest/search/v2?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7B7D2D77E4-CABF-4506-84FF-C3DC79854B74%7D%3Flang%3Den%26amp%3Bver%3D1&siteName=GoodSam&actionsHistory=%5B%5D&referrer=&visitorId=&isGuestUser=true&aq=(((%40fz95xpath79929%3D%3D7D2D77E4CABF450684FFC3DC79854B74%20%40fz95xtemplate79929%3D%3D57E2BFE90934466D93CD4A4405A15441)%20NOT%20%40fz95xtemplate79929%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B)))%20(((%24qf(function%3A%20%27dist(%40flocationlatitude79929%2C%40flocationlongitude79929%2C0%2C0)%2F%201609.344%27%2C%20fieldName%3A%20%27distance%27)%20%40distance%3C100000)%20OR%20(%40fstate79929%3D%3DKS))%20OR%20(%40flocationservices79929%3DKS))&cq=(%40fz95xlanguage79929%3D%3Den)%20(%40fz95xlatestversion79929%3D%3D1)%20(%40source%3D%3D%22GoodSam_coveo_web_index%20-%20sanford-coveo-prod%22)&searchHub=GSSLocationSearch&locale=en&maximumAge=9000000&firstResult=0&numberOfResults=1000&excerptLength=200&enableDidYouMean=true&sortCriteria=distance%20ascending&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&facetOptions=%7B%7D&categoryFacets=%5B%5D&retrieveFirstSentences=true"
        locations = session.get(base_url, headers=_headers).json()

        logger.info(f"{len(locations['results'])} locations found")

        for _ in locations["results"]:
            logger.info(_["clickUri"])
            page_url = str(_["clickUri"]).replace(":443", "")
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(
                " ".join(
                    sp1.select_one("div.location-info__info-col p").stripped_strings
                )
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = (
                sp1.select_one("div.swiper-slide iframe")["src"]
                .split("&q=")[1]
                .split("&z")[0]
                .split(",")
            )
            if "443" in page_url:
                raise
            yield SgRecord(
                page_url=page_url,
                location_name=_["Title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=coord[0],
                longitude=coord[1],
                phone=sp1.select_one("div.location-info__info-col h4").text,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
