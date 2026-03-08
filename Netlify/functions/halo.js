// halo.js - OPTICLENS Ice Crystal Halo Simulator API

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
    const halos = {
      '22°': {
        angle: 22,
        intensity: 0.85,
        description: 'Common halo from hexagonal ice crystals'
      },
      '46°': {
        angle: 46,
        intensity: 0.45,
        description: 'Rare halo from 90° prism faces'
      },
      circumzenithal: {
        angle: 90,
        intensity: 0.60,
        description: 'Colorful arc near zenith'
      },
      sun_dogs: {
        angle: 22,
        elevation: 0,
        intensity: 0.70,
        description: 'Bright spots at 22° from sun'
      }
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(halos)
    };

  } catch (error) {
    console.error('Error in halo function:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
