import geopandas as gpd
import pandas as pd
import os

class GRAL:
    """
    A class used to represent the GRAL module.

    Attributes:
        base_directory (str): The base directory for the project.
        met_file (str): The name of the met file.
        buildings_file (str): The name of the buildings file.
        line_file (str): The name of the line file.

    Methods:
        create_greb_file(bbox, horizontal_slices): Creates a GREB file with predefined values.
        create_in_dat_file(particles_ps, dispertion_time, latitude, horizontal_slices): Creates a in.dat file with predefined values.
        create_meteopgt_file(): Creates a meteopgt.all file with predefined values.
        create_pollutant_txt_file(pollutant): Creates a pollutant.txt file with predefined values.
        create_percent_file(): Creates a Percent.txt file with predefined values.
        create_max_proc_file(n_cores): Creates a Max_Proc.txt file with predefined values.
        create_other_txt_requiered_files(pollutant, n_cores): Creates the other txt requiered files with predefined values.
        create_buildings_file(): Creates a buildings.dat file with predefined values.
        create_line_emissions_file(pollutant): Creates a line.dat file with predefined values.
        create_met_time_series_data_file(meteo_file): Creates a mettimeseries.dat file with predefined values.
        create_dispersion_number_file(): Creates a DispNr.txt file with predefined values.
        create_other_optional_files(): Creates the other optional files with predefined values.
        get_number_of_weather_conditions(): Gets the number of weather conditions.
        rename_results(pollutant, horizontal_layers, n_meteo_conditions): Rename the results files.
    """

    def __init__(self, base_directory, met_file, buildings_file, line_file):
        """
        Initializes the GRAL class.

        Args:
            base_directory (str): The base directory for the project.
            met_file (str): The name of the met file.
            buildings_file (str): The name of the buildings file.
            line_file (str): The name of the line file.
        """
        self.base_directory = base_directory
        self.met_file = met_file
        self.buildings_file = buildings_file
        self.line_file = line_file

    #############################
    # REQUIRED FILES GENERATION #
    def create_greb_file(self, bbox, horizontal_slices) -> None:
        """
        Creates a GREB file with predefined values.

        Args:
            bbox (dict): A dictionary containing the bounding box coordinates.

        Returns:
            None
        """
        greb_file_path = f'{self.base_directory}/gral.geb'

        x_cell_size = 10
        y_cell_size = 10

        east_point = int(bbox['east'])
        west_point = int(bbox['west'])
        north_point = int(bbox['north'])
        south_point = int(bbox['south'])

        number_of_cells_x = int(abs(east_point - west_point) / x_cell_size)
        number_of_cells_y = int(abs(north_point - south_point) / y_cell_size)

        with open(greb_file_path, 'w') as file:
            file.write(
                f"{x_cell_size}              !cell-size for cartesian wind field in GRAL in x-direction\n")
            file.write(
                f"{y_cell_size}              !cell-size for cartesian wind field in GRAL in y-direction\n")
            file.write(
                "2,1.01              !cell-size for cartesian wind field in GRAL in z-direction, streching factor for increasing cells heights with height\n")
            file.write(
                f"{number_of_cells_x}              !number of cells for counting grid in GRAL in x-direction\n")
            file.write(
                f"{number_of_cells_y}              !number of cells for counting grid in GRAL in y-direction\n")
            file.write(
                f"{horizontal_slices}              !Number of horizontal slices\n")
            file.write(
                "1,              !Source groups to be computed seperated by a comma\n")
            file.write(
                f"{west_point}               !West border of GRAL model domain [m]\n")
            file.write(
                f"{east_point}               !East border of GRAL model domain [m]\n")
            file.write(
                f"{south_point}               !South border of GRAL model domain [m]\n")
            file.write(
                f"{north_point}              !North border of GRAL model domain [m]\n")

        print(f'GREB file created at: {greb_file_path}')

    def create_in_dat_file(self, particles_ps, dispertion_time, latitude, horizontal_slices) -> None:
        """
        Creates a in.dat file with predefined values.

        Args:
            particles_ps (int): Number of released particles per second.
            dispertion_time (int): Dispersion time.
            latitude (float): Latitude.
            horizontal_slices (list): List of horizontal slices.

        Returns:
            None
        """
        print('Creating in.dat file...')

        in_dat_file_path = f'{self.base_directory}/in.dat'
        with open(in_dat_file_path, 'w') as file:
            file.write(
                f"{particles_ps} \t ! Number of released particles per second\n")
            file.write(f"{dispertion_time} \t ! Dispersion time\n")
            file.write(
                "1 \t ! Steady state GRAL mode = 1, Transient GRAL mode = 0\n")
            file.write(
                "4 \t ! Meteorology input: inputzr.dat = 0, meteo.all = 1, elimaeki.prn = 2, SONIC.dat = 3, meteopgt.all = 4\n")
            file.write("0 \t ! Receptor points: Yes = 1, No = 0\n")
            file.write("0.2 \t ! Surface roughness in [m]\n")
            file.write(f"{round(float(latitude),2)} \t ! Latitude\n")
            file.write("N \t ! Meandering Effect Off = J, On = N\n")
            file.write(
                "NOx \t ! Pollutant: not used since version 19.01, new: Pollutant.txt\n")
            file.write(
                f"{','.join([str(slice) for slice in horizontal_slices])}, \t ! Horizontal slices [m] seperated by a comma (number of slices need to be defined in GRAL.geb!)\n")
            file.write("2 \t ! Vertical grid spacing in [m]\n")
            file.write(
                "1 \t ! Start the calculation with this weather number\n")
            file.write("2,15 \t ! How to take buildings into account? 1 = simple mass conservation, 2 = mass conservation with Poisson equation + advection, Factor for the prognostic sub domain size\n")
            file.write(
                "0 \t ! Stream output for Soundplan 1 = activated, -2 = write buildings height\n")
            file.write(
                "compressed V02 \t ! Write compressed output files\n")
            file.write(
                "WaitForKeyStroke \t ! Wait for keystroke when exiting GRAL\n")
            file.write(
                "ASCiiResults 1 \t ! Additional ASCii result files Yes = 1, No = 0\n")
            file.write(
                "0\t ! Adaptive surface roughness - max value [m]. Default: 0 = no adaptive surface roughness\n")
            file.write(
                "0\t ! Radius surrounding sources, in which the wind field is to be calculated prognostically; 0 = off, valid values: 50 - 10000 m\n")
            file.write("1 \t ! Use GRAL Online Functions = true\n")

        print(f'in.dat file created at: {in_dat_file_path}')

    def create_meteopgt_file(self) -> None:
        """
        Creates a meteopgt.all file with predefined values.

        Args:
            None

        Returns:
            None
        """
        print('Creating meteopgt.all file...')
        meteopgt_file_path = f'{self.base_directory}/meteopgt.all'

        meteo_conditions = {"wind_direction": [],
                            "wind_speed": [], "stability_class": []}
        with open(f'{self.base_directory}/{self.met_file}') as file:
            wind_direction = []
            wind_speed = []
            stability_class = []
            for line in file:
                # strip() is used to remove any leading/trailing whitespace, including newline characters
                content = line.strip()
                content = content.split(",")
                content.pop(0)
                content.pop(0)
                wind_speed.append(round(float(content[0]), 1))
                wind_direction.append(int(content[1]))
                stability_class.append(int(content[2]))

            meteo_conditions["wind_direction"] = wind_direction
            meteo_conditions["wind_speed"] = wind_speed
            meteo_conditions["stability_class"] = stability_class

        with open(meteopgt_file_path, 'w') as file:
            file.write(
                "10,0,10,    !Are dispersion situations classified =0 or not =1\n")
            file.write(
                "Wind direction sector,Wind speed class,stability class, frequency\n")
            for i in range(len(meteo_conditions["wind_speed"])):
                wind_direction = meteo_conditions["wind_direction"][i]
                divided_number = wind_direction / 10  # Step 1: Divide by 10
                multiplied_number = divided_number * 2  # Step 2: Multiply by 2
                # Step 3: Round to the nearest integer
                rounded_number = round(multiplied_number)
                wind_direction_sector = rounded_number / 2  # Step 4: Divide by 2
                file.write(
                    f"{wind_direction_sector},{wind_speed[i]},{stability_class[i]},1000\n")

        print(f'meteopgt.all file created at: {meteopgt_file_path}')

    def create_pollutant_txt_file(self, pollutant) -> None:
        """
        Creates a pollutant.txt file with predefined values.
        
        Args:
            pollutant (str): The name of the pollutant.
            
        Returns:
            None
        """
        print('Creating pollutant.txt file...')

        pollutant_file_path = f'{self.base_directory}/Pollutant.txt'
        with open(pollutant_file_path, 'w') as file:

            file.write(f"{pollutant}\n")
            file.write("0\t ! Wet deposition cW setting\n")
            file.write("0\t ! Wet deposition alphaW setting\n")
            file.write("0\t ! Decay rate for all source groups\n")

        print(f'Pollutant.txt file created at: {pollutant_file_path}')

    def create_percent_file(self) -> None:
        print('Creating percent file...')
        percent_file_path = f'{self.base_directory}/Percent.txt'
        with open(percent_file_path, 'w') as file:
            file.write("80")

        print(f'Percent.txt file created at: {percent_file_path}')

    def create_max_proc_file(self, n_cores) -> None:
        """
        Creates a Max_Proc.txt file with predefined values.

        Args:
            n_cores (int): Number of cores.

        Returns:
            None
        """
        print('Creating max_proc file...')
        max_proc_file_path = f'{self.base_directory}/Max_Proc.txt'
        with open(max_proc_file_path, 'w') as file:
            file.write(f"{n_cores}\n")

        print(f'Max_Proc.txt file created at: {max_proc_file_path}')

    def create_other_txt_requiered_files(self, pollutant, n_cores) -> None:
        """
        Execute the functions to create the other txt requiered files.

        Args:
            pollutant (str): The name of the pollutant.
            n_cores (int): Number of cores.

        Returns:
            None
        """
        print('Creating other txt requiered files...')
        self.create_pollutant_txt_file(pollutant)
        self.create_percent_file()
        self.create_max_proc_file(n_cores)

    #############################

    # OPTIONAL FILES GENERATION #

    def create_buildings_file(self) -> None:
        """
        Creates a buildings.dat file with predefined values.
        
        Args:
            None
        
        Returns:
            None
        """
        print('Creating buildings file...')
        buildings_gdf = gpd.read_file(f'{self.base_directory}/{self.buildings_file}')
        buildings_file_path = f'{self.base_directory}/buildings.dat'
        with open(buildings_file_path, 'w') as file:
            for index, row in buildings_gdf.iterrows():
                file.write(
                    f"{int(row['geometry'].centroid.x)},{int(row['geometry'].centroid.y)},0,{int(row['height'])}\n")

        print(f'buildings.dat file created at: {buildings_file_path}')

    def create_line_emissions_file(self, pollutant, is_online=False) -> None:
        """
        Creates a line.dat file with predefined values.
        
        Args:
            pollutant (str): The name of the pollutant.
            is_online (bool): If the process is online or offline.
        
        Returns:
            None
        """
        print('Creating line emissions file...')
        id= "osm_id"
        if not is_online:
            id = "edge_id"
        line_gdf = gpd.read_file(f'{self.base_directory}/{self.line_file}')
        line_file_path = f'{self.base_directory}/line.dat'
        with open(line_file_path, 'w') as file:
            file.write("Generated: \n")
            file.write("Generated: \n")
            file.write("Generated: \n")
            file.write(
                f"StrName,Section,Sourcegroup,x1,y1,z1,x2,y2,z2,width,noiseabatementwall,Length[km],--,{pollutant}[kg/(km*h)],--,--,--,--,--,deposition data\n")
            for index, row in line_gdf.iterrows():
                minx, miny, maxx, maxy = row['geometry'].bounds
                file.write(f'{row[id]},1,1,{round(minx,1)},{round(miny,1)},0,{round(maxx,1)},{round(maxy,1)},0,{row["width"]},-3,0,0,{convert_g_to_kg(float(row[f"{pollutant}_normed"]))},0,0,0,0,0,0,0,0,0,0,0,0,0\n')

        print(f'line.dat file created at: {line_file_path}')

    def create_met_time_series_data_file(self, meteo_file) -> None:
        """
        Creates a mettimeseries.dat file with predefined values.
        
        Args:
            meteo_file (str): The name of the meteo file (.met).
        
        Returns:
            None
        """
        print('Creating met time series data file...')
        met_time_series_data_file_path = f'{self.base_directory}/mettimeseries.dat'
        meteo_df = pd.read_csv(f'{self.base_directory}/{meteo_file}', sep=',', header=None)
        meteo_df.columns = ['day', 'time', 'wind_speed',
                            'wind_direction', 'stability_class']
        with open(met_time_series_data_file_path, 'w') as file:
            for index, row in meteo_df.iterrows():
                day_without_year = row['day'].split('.')[0]
                month_without_year = row['day'].split('.')[1]
                date = f"{day_without_year}.{month_without_year}"
                time_without_min = int(row['time'].split(':')[0]) # This is to prevent the 0 in front of the hour
                # Step 1: Divide by 10
                divided_number = float(row['wind_direction']) / 10
                multiplied_number = divided_number * 2  # Step 2: Multiply by 2
                # Step 3: Round to the nearest integer
                rounded_number = round(multiplied_number)
                wind_direction_sector = rounded_number / 2  # Step 4: Divide by 2
                file.write(
                    f"{date},{time_without_min},{int(row['wind_speed'])},{round(wind_direction_sector,1)},{int(row['stability_class'])}\n")

        print(
            f'mettimeseries.dat file created at: {met_time_series_data_file_path}')

    def create_dispersion_number_file(self) -> None:
        """
        Creates a DispNr.txt file with predefined values.
        
        Args:
            None
            
        Returns:
            None
        """
        print('Creating dispersion number file...')
        with open(f'{self.base_directory}/DispNr.txt', 'w') as file:
            file.write("1")

        print(f'DispNr.txt file created at: {self.base_directory}/DispNr.txt')

    def create_other_optional_files(self) -> None:
        """
        Execute the functions to create the other optional files.
        
        Args:
            None
        
        Returns:
            None
        """
        print('Creating other optional files...')
        self.create_met_time_series_data_file(self.met_file)
        self.create_dispersion_number_file()


    def get_number_of_weather_conditions(self) -> int:
        """
        Gets the number of weather conditions.
        
        Args:
            None
        
        Returns:
            int: The number of weather conditions.
        """
        meteo_df = pd.read_csv(f'{self.base_directory}/{self.met_file}', sep=',', header=None)
        meteo_df.columns = ['day', 'time', 'wind_speed',
                            'wind_direction', 'stability_class']
        return len(meteo_df)
    

    def rename_results(self, pollutant, horizontal_layers, n_meteo_conditions=1):
        """
        Rename the results files.

        Args:
            pollutant (str): The name of the pollutant.
            horizontal_layers (list): List of horizontal slices.
            n_meteo_conditions (int): Number of weather conditions.

        Returns:
            None
        """
        if n_meteo_conditions > 1:
            for i in range(1, n_meteo_conditions):
                if i < 10:
                    meteo_condition_txt_value = f"0000{i}"
                elif i < 100:
                    meteo_condition_txt_value = f"000{i}"
                elif i < 1000:
                    meteo_condition_txt_value = f"00{i}"
                else:
                    meteo_condition_txt_value = f"0{i}"

                    for n_horitonzal_layer in range(1, len(horizontal_layers)+1):
                        os.rename(f'{self.base_directory}/{meteo_condition_txt_value}-{n_horitonzal_layer}01.txt', f'{self.base_directory}/results_weather_{i}_{pollutant}_{horizontal_layers[n_horitonzal_layer-1]}m.txt')
        else:
            if len(horizontal_layers) > 1:
                for n_horitonzal_layer in range(1, len(horizontal_layers)+1):
                    os.rename(f'{self.base_directory}/00001-{n_horitonzal_layer}01.txt', f'{self.base_directory}/results_weather_{1}_{pollutant}_{horizontal_layers[n_horitonzal_layer-1]}m.txt')
            else:
                os.rename(f'{self.base_directory}/00001-101.txt', f'{self.base_directory}/results_weather_{1}_{pollutant}_{horizontal_layers[0]}m.txt')
    ################################


def convert_g_to_kg(g) -> float:
    return g / 1000
