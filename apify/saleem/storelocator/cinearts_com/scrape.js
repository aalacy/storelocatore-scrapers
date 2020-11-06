const Apify = require('apify');

async function enqueueLocationLinks({ $, requestQueue }) {
  return Apify.utils.enqueueLinks({
    $,
    requestQueue,
    baseUrl: 'https://cinemark.com/',
    selector: '.theatres-by-state a',
    pseudoUrls: [new Apify.PseudoUrl(/cine?arts/)],
  });
}

function scrapeLatLng($) {
  const src = $('.theatreMap img').attr('data-src');
  const match = src.match(/pp=(.*),(.*)&/i);
  if (match) {
    const [_, latitude, longitude] = match;
    return { latitude, longitude };
  } else {
    return {};
  }
}

async function scrape({ $, request }) {
  const scripts = $('script[type="application/ld+json"]');
  const status = $('.theatre-status-label').text();

  if (status.match(/closed/i)) {
    return null;
  }

  const targetScript = scripts.length > 1 ? scripts[1] : scripts[0];
  try {
    const data = JSON.parse(targetScript.children[0].data);
    const {
      name: location_name,
      address: [
        {
          streetAddress: street_address,
          addressLocality: city,
          addressRegion: state,
          postalCode: zip,
          addressCountry: country_code,
        },
      ],
      email,
      telephone: phone,
    } = data;

    const { latitude, longitude } = scrapeLatLng($);
    const location_type = 'CinéArts';
    const store_number = parseInt(email.split('@')[0]);

    return {
      locator_domain: 'cinearts.com',
      page_url: request.url,
      location_name,
      street_address,
      city,
      state,
      zip,
      country_code,
      store_number,
      phone: phone || '<MISSING>',
      location_type,
      latitude: latitude || '<MISSING>',
      longitude: longitude || '<MISSING>',
      hours_of_operation: '<MISSING>',
    };
  } catch (err) {
    return null;
  }
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'https://www.cinemark.com/full-theatre-list',
    userData: {
      pageType: 'locations',
    },
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    ignoreSslErrors: true,
    async handlePageFunction({ request, $ }) {
      switch (request.userData.pageType) {
        case 'locations':
          await enqueueLocationLinks({ $, requestQueue });
          break;
        default:
          const poi = await scrape({ $, request });
          if (poi) await Apify.pushData(poi);
      }
    },
  });

  await crawler.run();
});
