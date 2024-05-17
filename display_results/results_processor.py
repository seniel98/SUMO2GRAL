import numpy as np
import pandas as pd
import sys
import plotly.express as px
import geopandas as gpd
import pyproj

# Path: local_files_processor/local_file_processor.py


class ResultsProcessor:

    def __init__(self):
        """
        Initialize the ResultsProcessor class

        """

    def read_results_file(self, results_file):
        """
        Read the results file

        Args:
            results_file (str): The path to the results file

        Returns:
            lines (list): The list of the lines of the results file
        """
        with open(results_file, 'r') as f:
            lines = f.readlines()
        return lines
    
    def extract_results_header_info(self, lines):
        """
        Extract the header information of the results file

        Args:
            lines (list): The list of the lines of the results file

        Returns:
            ncols (int): The number of columns
            nrows (int): The number of rows
            xllcorner (float): The xllcorner
            yllcorner (float): The yllcorner
            cellsize (float): The cellsize
            nodata (float): The nodata value
        """
        ncols = int(lines[0].split()[1])
        nrows = int(lines[1].split()[1])
        xllcorner = float(lines[2].split()[1])
        yllcorner = float(lines[3].split()[1])
        cellsize = float(lines[4].split()[1])
        nodata = float(lines[5].split()[1])
        
        return ncols, nrows, xllcorner, yllcorner, cellsize, nodata

    def extract_pollutant_data(self, lines, nodata):
        """
        Extract the pollutant data

        Args:
            lines (list): The list of the lines of the results file
            nodata (float): The nodata value

        Returns:
            data_pollutant (np.array): The data of the pollutant
        """
        data_pollutant = np.array([list(map(float, line.split())) for line in lines[6:]])
        # Replace nodata values with np.nan
        data_pollutant[data_pollutant == nodata] = np.nan
        return data_pollutant

    def gather_coordinates_and_values(self, data_pollutant, ncols, nrows, xllcorner, yllcorner, cellsize):
        """
        Gather the coordinates

        Args:
            data_pollutant (np.array): The data of the pollutant
            ncols (int): The number of columns
            nrows (int): The number of rows
            xllcorner (float): The xllcorner
            yllcorner (float): The yllcorner
            cellsize (float): The cellsize

        Returns:
            x (np.array): The x coordinates
            y (np.array): The y coordinates
            data (np.array): The data values
        """
        x_values = []
        y_values = []
        data_values = []
        # Gather coordinates and values in lists for pollutant data
        for i in range(nrows):
            for j in range(ncols):
                x = xllcorner + j * cellsize
                y = yllcorner + i * cellsize
                value = data_pollutant[i, j]
                
                if not np.isnan(value):  # Exclude NaN values
                    x_values.append(x)
                    y_values.append(y)
                    data_values.append(value)
        
        x = np.array(x_values)
        y = np.array(y_values)
        data = np.array(data_values)
        return x, y, data

    def convert_coordinates(self, x, y, src_crs, dst_crs):
        """
        Convert x, y coordinates from src_crs to dst_crs using pyproj.
        
        Parameters:
        - x, y: Arrays or lists of x and y coordinates.
        - src_crs: Source coordinate reference system (EPSG code).
        - dst_crs: Target coordinate reference system (EPSG code).
        
        Returns:
        - x_out, y_out: Arrays of transformed x and y coordinates.
        """
        transformer = pyproj.Transformer.from_crs("EPSG:{}".format(src_crs), "EPSG:{}".format(dst_crs), always_xy=True)
        x_out, y_out = transformer.transform(x, y)
        return x_out, y_out

    def graph_results(self, df, pollutant, mapbox_api_key, type='scattermapbox'):
        """
        Graph the results

        Args:
            df (pd.DataFrame): The DataFrame of the results
            pollutant (str): The name of the pollutant
            mapbox_api_key (str): The mapbox api key
            type (str): The type of the graph

        Returns:
            None
        """
        px.set_mapbox_access_token(mapbox_api_key)

        if type == 'scattermapbox':
            df['size'] = 1
            fig = px.scatter_mapbox(df, lat="lat", lon="lon", color=pollutant,
                                    color_continuous_scale='Temps', zoom=12, range_color=(min(df[f'{pollutant}']), max(df[f'{pollutant}'])), opacity=0.1, size='size')
            # Update label of scale bar 
            fig.update_layout(coloraxis_colorbar=dict(title=f"{pollutant} (µg/m³)"))
            return fig
        elif type == 'densitymapbox':
            fig = px.density_mapbox(df, lat='lat', lon='lon', z='data', radius=10, zoom=12.5,
                                    color_continuous_scale='Temps', range_color=(min(df[f'{pollutant}']), max(df[f'{pollutant}'])))
            # Update label of scale bar
            fig.update_layout(coloraxis_colorbar=dict(title=f"{pollutant} (µg/m³)"))
            return fig
        else:
            raise Exception(f"Invalid type. The type must be scattermapbox or densitymapbox, and is {type}")
        
        return None

    
    def process_results(self, results_file, mapbox_api_key, type, src_crs=3857, dst_crs=4326):
        """
        Process the results file

        Args:
            results_file (str): The path to the results file
            mapbox_api_key (str): The mapbox api key
            type (str): The type of the graph
            src_crs (int): The source coordinate reference system (EPSG code)
            dst_crs (int): The destination coordinate reference system (EPSG code)

        Returns:
            None
        """
        # Get the name of the pollutant from the results file, results_weather_1_CO_1.5m.txt -> CO
        pollutant = results_file.split('_')[3]
        lines = self.read_results_file(results_file)
        ncols, nrows, xllcorner, yllcorner, cellsize, nodata = self.extract_results_header_info(lines)
        data_pollutant = self.extract_pollutant_data(lines, nodata)
        x, y, data = self.gather_coordinates_and_values(data_pollutant, ncols, nrows, xllcorner, yllcorner, cellsize)
        x, y = self.convert_coordinates(x, y, src_crs, dst_crs)

        df = pd.DataFrame({'lon': x, 'lat': y, f'{pollutant}': data})

        # # Remove all rows with data value 0
        df = df[df[f'{pollutant}'] != 0.0]

        # Reduce precision of coordinates
        decimal_places = 3
        df['lon'] = df['lon'].round(decimal_places)
        df['lat'] = df['lat'].round(decimal_places)

        # Aggregate data by coordinates
        df_aggregated = df.groupby(['lon', 'lat']).mean().reset_index()

        # Plot the results
        fig = self.graph_results(df_aggregated, pollutant, mapbox_api_key, type=type)
        if fig is not None:
            fig.show()
