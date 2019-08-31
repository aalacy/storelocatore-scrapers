const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

(async () => {
  const sources = [];
  const rootAddress = new URL('https://coreevolutionpb.com/index.html');
  const $ = cheerio.load(await request.get(rootAddress.href));
  $('.SubMenu a').each((_, elem) => {
    sources.push({ url: (new URL($(elem).attr('href'), rootAddress.origin)).href});
  })
  const requestList = new Apify.RequestList({ sources });
  await requestList.initialize();

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: async ({ request, response, html, $ }) => {

      // Begin scraper
      const info = $('.Header-small');
      const {
        city,
        state,
        zip
      } = $(info[4]).text().match(/^[\s\n]*(?<city>.*),\s(?<state>[A-Z]{2})\s(?<zip>[\d-]{5,10})[\s\n]*$/).groups;
      const {
        latitude,
        longitude
      } = $('iframe').attr('src').match(/\!2d(?<longitude>-?\d{2}\.\d+)\!3d(?<latitude>-?\d{2}\.\d+)\!/).groups;
			const poi = {
        locator_domain: 'coreevolutionpb.com',
        location_name: $('title').text().trim(),
        street_address: $(info[3]).text().trim(),
        city,
        state,
        zip,
        country_code: 'US',
				store_number: '<MISSING>',
				phone: $(info[0]).text().trim(),
				location_type: '<MISSING>',
        latitude,
        longitude,
				hours_of_operation: '<MISSING>'
			};

			await Apify.pushData([poi]);

			// End scraper

    },
  });

  await crawler.run();
})();
