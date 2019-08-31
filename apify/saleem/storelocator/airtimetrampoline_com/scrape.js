const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

(async () => {
  const rootAddress = new URL('https://airtimetrampoline.com/locations/');
  const $ = cheerio.load(await request.get(rootAddress.href));
  const sources = $('.fl-button-wrap a').map((_, elem) => { return { url: $(elem).attr('href') }; }).get()
  const requestList = new Apify.RequestList({
    sources,
  });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

      // Begin scraper
      
      const headingElements = $('.fl-heading');
      const {street_address, city, state, zip, country} = headingElements.eq(1).text().trim().match(
        /^(?<street_address>.{3,}),\s(?<city>.{2,}),\s(?<state>[A-Z]{2})\s(?<zip>[\d\s]{5,10}),\s(?<country>[A-Z]{2,})$/
      ).groups

			const poi = {
        locator_domain: 'airtimetrampoline.com',
        location_name: headingElements.eq(0).text().trim(),
        street_address,
        city,
        state,
        zip,
        country_code: country.slice(0,2),
				store_number: '<MISSING>',
				phone: headingElements.eq(2).text().trim(),
				location_type: '<MISSING>',
        latitude: '<MISSING>',
        longitude: '<MISSING>',
				hours_of_operation: $('.pp-icon-list-items').eq(0).text().trim().replace(/[\n\t\s]+/g, ' ')
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();
