# 🔭 OPTICLENS Shell Completion

OPTICLENS provides shell completion for bash, zsh, and fish shells.

---

## Installation

### Bash
```bash
eval "$(_OPTICLENS_COMPLETE=bash_source opticlens)"
```

Zsh

```zsh
eval "$(_OPTICLENS_COMPLETE=zsh_source opticlens)"
```

Fish

```fish
eval (env _OPTICLENS_COMPLETE=fish_source opticlens)
```

---

Available Commands

Core Commands

Command Description
opticlens mie Calculate Mie scattering parameters
opticlens edlen Compute refractive index (Edlén equation)
opticlens turbulence Calculate turbulence parameters (Cn2, r0, σχ²)
opticlens radiative Run radiative transfer calculations
opticlens mirage Simulate mirage displacement
opticlens halo Generate ice crystal halo patterns
opticlens dashboard Launch interactive dashboard
opticlens stations List AERONET stations

Physics Commands

```bash
opticlens mie --radius 0.1 --wavelength 0.55          # Mie efficiencies
opticlens edlen --pressure 101325 --temp 288.15       # Refractive index
opticlens turbulence --cn2 1e-15 --path 1000          # Scintillation
opticlens radiative --aod 0.2 --zenith 30              # Radiative transfer
```

Simulation Commands

```bash
opticlens mirage --temp-gradient 0.5 --path 1000       # Mirage displacement
opticlens halo --crystal plate --angle 22              # 22° halo simulation
opticlens ray-trace --profile standard                  # Ray tracing through atmosphere
```

Data Commands

```bash
opticlens stations list                                 # List all AERONET stations
opticlens stations show --name "GSFC"                   # Show station details
opticlens data fetch --source aeronet --station GSFC    # Fetch AERONET data
opticlens data compare --station1 GSFC --station2 Lille # Compare two stations
```

Wavelength Commands

```bash
opticlens wavelengths list                               # List standard wavelengths
opticlens wavelengths --range 0.4-0.7 --step 0.01       # Generate wavelength array
```

Alert Thresholds

```bash
opticlens alert --status quiet          # AOD 0-0.1 ⚪
opticlens alert --status caution        # AOD 0.1-0.3 🟢
opticlens alert --status watch          # AOD 0.3-0.5 🟡
opticlens alert --status warning        # AOD 0.5-0.8 🟠
opticlens alert --status critical       # AOD >0.8 🔴
```

---

Examples

```bash
# Calculate Mie scattering for fine mode aerosol
opticlens mie --radius 0.1 --wavelength 0.55 --refractive-index 1.5+0.01j

# Get refractive index at standard conditions
opticlens edlen --pressure 101325 --temperature 288.15 --wavelength 0.55 --humidity 0.5

# Calculate turbulence parameters
opticlens turbulence --cn2 1e-15 --wavelength 0.55 --path 1000 --output json

# Simulate mirage over desert
opticlens mirage --temp-gradient 0.8 --path 2000 --observer-height 1.7

# Generate 22° halo
opticlens halo --type 22-degree --crystal-type hexagonal --output halo.png

# Fetch real-time AERONET data
opticlens data fetch --source aeronet --station GSFC --hours 24

# Launch dashboard
opticlens dashboard --port 8501 --map-type aerosol

# Compare two stations
opticlens stations compare --s1 GSFC --s2 Lille --parameter AOD_500nm
```

---

Tab Completion Features

Wavelength Completion

· 0.34 μm (UV)
· 0.44 μm (blue)
· 0.55 μm (green)
· 0.67 μm (red)
· 0.87 μm (NIR)
· 1.02 μm (NIR)
· 1.64 μm (SWIR)

AERONET Station Completion

· GSFC (Maryland, USA)
· Lille (France)
· Barcelona (Spain)
· Osaka (Japan)
· Canberra (Australia)
· Skukuza (South Africa)
· Manaus (Brazil)
· And 500+ more stations

Parameter Completion

· Physical: mie, edlen, turbulence, radiative
· Simulation: mirage, halo, ray-trace
· Data: fetch, compare, plot, export

Alert Status Colors

· ⚪ QUIET      (AOD 0.0-0.1)
· 🟢 CAUTION    (AOD 0.1-0.3)
· 🟡 WATCH      (AOD 0.3-0.5)
· 🟠 WARNING    (AOD 0.5-0.8)
· 🔴 CRITICAL   (AOD >0.8)

---

Environment Variables

```bash
export OPTICLENS_CONFIG=~/.opticlens/config.yaml
export OPTICLENS_DATA_DIR=/data/opticlens
export NASA_EARTHDATA_TOKEN=your_token_here
export AERONET_API_KEY=your_key_here
export MODIS_API_KEY=your_key_here
export CALIPSO_API_KEY=your_key_here
```

---

Live Resources

· Dashboard: https://opticlens.netlify.app
· Documentation: https://opticlens.readthedocs.io
· AERONET: https://aeronet.gsfc.nasa.gov
· MODIS: https://modis.gsfc.nasa.gov
· CALIPSO: https://www-calipso.larc.nasa.gov

---

🔭 Light does not simply travel through the atmosphere — it is shaped, scattered, bent, and dispersed by it.
