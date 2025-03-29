# SUMO2GRAL (S2G) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/MIT)

S2G is a project aimed at simplifying the workflow of estimating pollutant concentrations in urban areas by automating the simulation process in [GRAL (Graz Lagrangian Model)](https://gral.tugraz.at/). By providing geographic area specifications or an Open Street Map (OSM) file, [SUMO (Simulation of Urban MObility) emissions files](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html), and weather data for the desired area, users can effortlessly perform GRAL simulations and obtain pollutant concentrations for the studied area. The weather data format aligns with the format provided by the [monitor stations of Valencian Environmental Agency](https://mediambient.gva.es/es/web/calidad-ambiental/datos-on-line).

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Dependencies](#dependencies)
- [Setup](#setup)
- [Usage](#usage)
- [Documentation](#documentation)
- [Tutorials](#tutorials)
  - [Use Case: Wildau](#use-case-wildau)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

## Features

- **Automated Data Processing**: Simplifies the preparation of input files for GRAL by automatically processing building, weather, highway, and map data.
- **Georeferenced Map Generation**: Creates georeferenced maps based on specified geographic bounds.
- **Shapefile Generation**: Generates shapefiles for buildings and highways which are essential for GRAL simulations.
- **Weather Data Processing**: Processes weather data to match the requirements of GRAL simulations.
- **GRAL Files Generation**: Automates the creation of required GRAL simulation files through a dedicated module.
- **GRAL Simulation**: Executes the GRAL simulation and outputs the reuslts in a .txt file.
- **Pollutant Concentration Analysis**: Provides a module for analyzing pollutant concentrations in the studied area.

## Prerequisites

You must have installed the Dotnet >= 6.0 SDK installed. Please visit the [Windows .NET 8.0 downloading page](https://dotnet.microsoft.com/en-us/download/dotnet/8.0).

If you are a Linux user you can simply do:

```bash
sudo apt-get install -y dotnet-sdk-8.0
```

## Dependencies

- pandas
- osmnx
- sumolib
- numpy
- geopandas
- cartopy
- pyproj
- osmium

## Setup

Clone the repository:

```bash
git clone https://github.com/seniel98/SUMO2GRAL.git
cd SUMO2GRAL
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the command line interface (CLI) script with the desired arguments to process the data and generate the required files:

Offline mode (*default*):

- Parameters mode

  ```bash
  python cli.py --base-directory /path/to/base/directory --process all --osm-file /path/to/osm/file/file.osm  --net-file /path/to/net/file/file.net.xml --emissions-file /path/to/edge/emissions/file/edges-emissions-file.xml --gral-dll /path/to/gral/dll/file/GRAL.dll
  ```

- Configuration file mode (here you can take a look at the structure of the [config file](/examples/configuration.sumo2gral.cfg))

  ```bash
  python cli.py -c configuration.sumo2gral.cfg --process all
  ```

Online mode (This is in case you want to retrieve the data using the osmnx library):

```bash
python cli.py --base-directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --process all  --net-file /path/to/net/file/file.net.xml --emissions-file /path/to/edge/emissions/file/edges-emissions-file.xml --online --gral-dll /path/to/gral/dll/file/GRAL.dll
```

After the data processing is complete, you can display the pollutant concentrations in the studied area:

```bash
python cli.py --process results --display-geo-map -r /path/to/results/file/results.txt --mapbox-api-key your_mapbox_api_key
```

This command displays the pollutant concentration map using Mapbox. Replace `your_mapbox_api_key` with your API key (see how to [create your API KEY](https://docs.mapbox.com/help/getting-started/access-tokens/)).

## Documentation

For a comprehensive guide to S2G's architecture and modules, refer to the in-depth [documentation here](https://seniel98.github.io/SUMO2GRAL/).

## Tutorials

### Use Case: Wildau

This tutorial provides a step-by-step guide on using SUMO2GRAL with data from Wildau, Germany. It covers everything from setting up your environment and running SUMO simulations to executing GRAL simulations and analyzing the results. This example serves as a practical illustration of how SUMO2GRAL can be applied to real-world scenarios.

[View the Wildau Tutorial](/examples/Wildau/README.md)

For more detailed examples and use cases, please check our [documentation](https://seniel98.github.io/SUMO2GRAL/).

## Contributing

Your contributions are welcome! Please refer to the [contributing guidelines](CONTRIBUTING.md) for more information.

## Citation

Please cite [this article](http://dx.doi.org/10.1109/DS-RT62209.2024.00016) if you use this tool during your research.

Bibtex reference:
```tex
@INPROCEEDINGS{10937689,
  author={Padrón, José D. and Behrisch, Michael and Calafate, Carlos T.},
  booktitle={2024 28th International Symposium on Distributed Simulation and Real Time Applications (DS-RT)}, 
  title={SUMO2GRAL: A tool to simplify the workflow of estimating pollutant concentrations in urban areas}, 
  year={2024},
  volume={},
  number={},
  pages={42-47},
  keywords={Atmospheric modeling;Urban areas;Focusing;Air pollution;Real-time systems;Reliability;Dispersion;Air pollution;SUMO;GRAL;vehicle emissions;traffic pollution},
  doi={10.1109/DS-RT62209.2024.00016}}
```

## License

S2G is made available under the [MIT License](https://opensource.org/license/mit).
