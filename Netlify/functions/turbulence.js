// turbulence.js - OPTICLENS Optical Turbulence API

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
    const turbulence = {
      Cn2: 1.5e-15,
      fried_parameter: 0.12,
      scintillation_index: 0.08,
      coherence_time: 0.005,
      isoplanatic_angle: 2.3,
      greenwood_frequency: 45.6,
      timestamp: new Date().toISOString()
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(turbulence)
    };

  } catch (error) {
    console.error('Error in turbulence function:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
