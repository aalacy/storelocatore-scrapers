const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

(async () => {
  const rootAddress = new URL('https://barneysbeanery.com/locations/');
  const rootPage = await request.get(rootAddress.href);
  const $ = cheerio.load(rootPage)
  const sources = $('.location .entry-thumbnail a').map((_, elem) => {
    return { url: $(elem).attr('href')}
  }).get();
  const requestList = new Apify.RequestList({
    sources
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

      // Begin scraper
      const dataArea = $('.entry-content .content-area');
      const {street_address, city, state, zip, phone} = $('p', dataArea).first().text().trim().match(
        /^(?<street_address>[\d\D]*)\n(?<city>.*),?\s(?<state>[A-Z]{2})\s(?<zip>[\d-]*)\n(?<phone>[\d\(\)-\s]*)$/
      ).groups;

			const poi = {
        locator_domain: 'barneysbeanery.com',
        location_name: $('title').text().trim(),
        street_address,
        city,
        state,
        zip,
        country_code: 'US',
				store_number: '<MISSING>',
				phone,
				location_type: '<MISSING>',
        latitude: '<MISSING>',
        longitude: '<MISSING>',
				hours_of_operation: $('p', dataArea).eq(1).text().trim()+' '+$('p', dataArea).eq(2).text().trim()
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();
