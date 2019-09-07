const Apify = require('apify');

const enqueueRegionClubPages = async (page, requestQueue, request) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: '#main > div.container.content-container > section > div > div > ul:nth-child(11) a',
  pseudoUrls: [
    'https://[.*]/clubs/',
  ],
  userData: {
    urlType: 'region',
  },
});

module.exports = {
  enqueueRegionClubPages,
};
