from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("woknfire")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("\u200b", "").strip()


def fetch_data():
    locator_domain = "https://www.woknfire.com/"
    page_url = "https://www.woknfire.com/contact-locations"
    base_url = "https://siteassets.parastorage.com/pages/pages/thunderbolt?beckyExperiments=specs.thunderbolt.addressInputAtlasProvider%3Atrue%2Cspecs.thunderbolt.seoFriendlyDropDownMenu%3Atrue%2Cspecs.thunderbolt.FileUploaderPopper%3Atrue%2Ctb_UploadButtonFixValidationNotRequired%3Atrue%2Cspecs.thunderbolt.breakingBekyCache%3Atrue%2Cspecs.thunderbolt.ResponsiveInClassic%3Atrue%2Cspecs.thunderbolt.tb_media_layout_by_effect%3Atrue&contentType=application%2Fjson&deviceType=Desktop&dfCk=6&dfVersion=1.1273.0&experiments=bv_cartPageResponsiveLayoutFixer%2Cbv_migrateResponsiveLayoutToSingleLayoutData%2Cbv_migrateResponsiveToVariantsModels%2Cbv_removeMenuDataFromPageJson%2Cbv_remove_add_chat_viewer_fixer%2Cdm_fixMobileHoverBoxDesign&externalBaseUrl=https%3A%2F%2Fwww.woknfire.com&fileId=0b34693c.bundle.min&hasTPAWorkerOnSite=false&isHttps=true&isInSeo=false&isMultilingualEnabled=false&isPremiumDomain=true&isUrlMigrated=true&isWixCodeOnPage=false&isWixCodeOnSite=false&language=en&languageResolutionMethod=QueryParam&metaSiteId=d37e737d-e347-48ab-b17b-96402a95ae23&module=thunderbolt-features&originalLanguage=en&pageId=b8358d_ceab2b92b9712ed3811c6084c47afdda_826.json&quickActionsMenuEnabled=false&registryLibrariesTopology=%5B%7B%22artifactId%22%3A%22editor-elements%22%2C%22namespace%22%3A%22wixui%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.6047.0%22%7D%2C%7B%22artifactId%22%3A%22editor-elements-design-systems%22%2C%22namespace%22%3A%22dsgnsys%22%2C%22url%22%3A%22https%3A%2F%2Fstatic.parastorage.com%2Fservices%2Feditor-elements%2F1.6047.0%22%7D%5D&remoteWidgetStructureBuilderVersion=1.226.0&siteId=4629e65a-dc4e-49ee-9c86-4313e7e4b5c3&siteRevision=847&staticHTMLComponentUrl=https%3A%2F%2Fwww-woknfire-com.filesusr.com%2F&tbElementsSiteAssets=siteAssets.8d1e3854.bundle.min.js&useSandboxInHTMLComp=false&viewMode=desktop"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["props"]["render"][
            "compProps"
        ]
        logger.info(f"{len(locations)} found")
        has_name = False
        for key, loc in locations.items():
            if loc.get("name"):
                has_name = True
            if loc.get("skin") != "WRichTextNewSkin":
                continue
            if not has_name:
                continue
            has_name = False
            _ = bs(loc["html"], "lxml")
            if not _.h6:
                continue
            addr = [aa.text.strip() for aa in _.select("h6 span")][1:]
            temp = [hh.text.strip() for hh in _.select("p") if _valid(hh.text)]
            hours = []
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            street_address = addr[0]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=page_url,
                location_name=_.span.text.strip(),
                street_address=street_address,
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
