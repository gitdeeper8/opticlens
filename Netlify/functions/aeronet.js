// aeronet.js - OPTICLENS AERONET Stations API

exports.handler = async (event, context) => {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': 'https://opticlens.netlify.app',
    'Access-Control-Allow-Headers': 'Content-Type'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  try {
    const stations = [
      { name: 'GSFC', lat: 38.992, lon: -76.840, altitude: 87, country: 'USA', aod: 0.12 },
      { name: 'Lille', lat: 50.611, lon: 3.141, altitude: 60, country: 'France', aod: 0.15 },
      { name: 'Barcelona', lat: 41.386, lon: 2.117, altitude: 125, country: 'Spain', aod: 0.18 },
      { name: 'Osaka', lat: 34.651, lon: 135.591, altitude: 50, country: 'Japan', aod: 0.25 },
      { name: 'Canberra', lat: -35.282, lon: 149.128, altitude: 577, country: 'Australia', aod: 0.05 },
      { name: 'Skukuza', lat: -24.992, lon: 31.587, altitude: 150, country: 'South Africa', aod: 0.32 },
      { name: 'Manaus', lat: -2.890, lon: -59.970, altitude: 110, country: 'Brazil', aod: 0.45 }
    ];

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(stations)
    };

  } catch (error) {
    console.error('Error in aeronet function:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
