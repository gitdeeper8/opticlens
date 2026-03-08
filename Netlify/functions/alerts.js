// alerts.js - OPTICLENS Atmospheric Alerts API

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
    const alerts = [
      {
        id: 'AOD-20260308-001',
        time: '08:45 UTC',
        level: 'WARNING',
        aod: 0.67,
        description: 'High aerosol optical depth detected',
        location: 'Beijing, China',
        type: 'aerosol'
      },
      {
        id: 'TURB-20260308-002',
        time: '14:20 UTC',
        level: 'CAUTION',
        cn2: 2.3e-15,
        description: 'Increased turbulence',
        location: 'Mauna Kea, Hawaii',
        type: 'turbulence'
      },
      {
        id: 'HALO-20260308-003',
        time: '22:15 UTC',
        level: 'INFO',
        description: '22° halo observed',
        location: 'Antarctica',
        type: 'halo'
      }
    ];

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(alerts)
    };

  } catch (error) {
    console.error('Error in alerts function:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
