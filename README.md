# SUMO-GRAL: Urban Pollutants Concentration Estimator

SUMO-GRAL is a project aimed at simplifying the process of estimating pollutant concentrations in urban areas by automating the preparation of necessary files for simulation in [GRAL (Graz Lagrangian Model)](https://gral.tugraz.at/). By providing geographic area specifications, [SUMO (Simulation of Urban MObility) emissions files](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html), and weather data for the desired area, users can effortlessly generate the required files for conducting GRAL simulations. The weather data format aligns with the format provided by the [monitor stations of Valencian Environmental Agency](https://mediambient.gva.es/es/web/calidad-ambiental/datos-on-line).

## Features

- **Automated Data Processing**: Simplifies the preparation of input files for GRAL by automatically processing building, weather, highway, and map data.
- **Georeferenced Map Generation**: Creates georeferenced maps based on specified geographic bounds.
- **Shapefile Generation**: Generates shapefiles for buildings and highways which are essential for GRAL simulations.
- **Weather Data Processing**: Processes weather data to match the requirements of GRAL simulations.

## Dependencies

- pandas
- osmnx
- sumolib
- numpy
- geopandas
- cartopy
- pyproj

## Setup

Clone the repository:

```bash
git clone https://github.com/seniel98/SUMO-GRAL.git
cd SUMO-GRAL
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the command line interface (CLI) script with the desired arguments to process the data and generate the required files:

```bash
python CLI.py --base_directory /path/to/base/directory --north 39.49 --south 39.47 --east -0.37 --west -0.39 --epsg 3857 --process all
```

## Documentation

### Modules

- `buildings_processor.py`: Processes building data to create shapefiles.
- `weather_processor.py`: Processes weather data to match the format required for GRAL simulations.
- `highway_data_processor.py`: Processes highway data to create shapefiles and processes SUMO emissions files.
- `maps_processor.py`: Generates georeferenced maps based on the specified geographic bounds.
- `main.py`: Orchestrates the data processing based on user inputs.
- `cli.py`: Provides a command line interface for the project.

### CLI Arguments

- `--base_directory`: The base directory for the project.
- `--north`, `--south`, `--east`, `--west`: The coordinates of the bounding box.
- `--epsg`: The EPSG code for the coordinate system to reproject the map to.
- `--process`: Specify the process to run. Choices are: map, buildings, weather, highway.
- `--map_name`: The name of the map file to be saved.
- `--buildings_shp_file`: The name of the shapefile to be saved.
- `--highways_shp_file`: The name of the shapefile to be saved.
- `--net_file`: The name of the SUMO network file.
- `--emissions_file`: The name of the SUMO emissions file.
- `--weather_file`: The name of the weather data file.
- `--weather_day`: The day of the weather data to extract, format (dd.mm.yyyy).
- `--weather_hour`: The hour of the weather data to extract, format (hh:mm).

## Contributing

Contributions are welcome! Create a new issue to discuss a feature or bug, or create a pull request to propose changes.

## License

This project is licensed under the [MIT License](LICENSE).
