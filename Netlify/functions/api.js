// api.js - OPTICLENS Main API Entry Point
// Optical Phenomena, Turbulence & Imaging — Light Environmental Nonlinearity System

exports.handler = async function(event, context) {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': 'https://opticlens.netlify.app'
    },
    body: JSON.stringify({
      message: '🔭 Welcome to OPTICLENS API!',
      description: 'Optical Phenomena, Turbulence & Imaging — Light Environmental Nonlinearity System',
      version: '10.0.0',
      doi: '10.5281/zenodo.18907508',
      status: 'operational',
      mie_accuracy: '0% error vs Bohren & Huffman (1983)',
      endpoints: {
        mie: '/.netlify/functions/mie',
        aeronet: '/.netlify/functions/aeronet',
        turbulence: '/.netlify/functions/turbulence',
        halo: '/.netlify/functions/halo',
        mirage: '/.netlify/functions/mirage',
        stations: '/.netlify/functions/stations',
        alerts: '/.netlify/functions/alerts'
      },
      documentation: 'https://opticlens.readthedocs.io',
      dashboard: 'https://opticlens.netlify.app',
      pypi: 'https://pypi.org/project/opticlens/',
      timestamp: new Date().toISOString()
    })
  };
};
