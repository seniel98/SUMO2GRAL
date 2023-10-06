

class GRAL:

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
                "compressed V02 \t ! Write strong compressed output files\n")
            file.write(
                "WaitForKeyStroke \t ! Wait for keystroke when exiting GRAL\n")
            file.write(
                "ASCiiResults 0 \t ! Additional ASCii result files Yes = 1, No = 0\n")
            file.write(
                "0\t ! Adaptive surface roughness - max value [m]. Default: 0 = no adaptive surface roughness\n")
            file.write(
                "0\t ! Radius surrounding sources, in which the wind field is to be calculated prognostically; 0 = off, valid values: 50 - 10000 m\n")
            file.write("1 \t ! Use GRAL Online Functions = true\n")

        print(f'in.dat file created at: {in_dat_file_path}')

    def create_meteogpt_file(self, met_file) -> None:
        print('Creating meteogpt.all file...')
        meteogpt_file_path = f'{self.base_directory}/meteogpt.all'

        meteo_conditions = {"wind_direction": [],
                            "wind_speed": [], "stability_class": []}
        with open(met_file, 'r') as file:
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

        with open(meteogpt_file_path, 'w') as file:
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
                
        print(f'meteogpt.all file created at: {meteogpt_file_path}')

    def create_pollutant_txt_file(self, pollutant) -> None:
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
        print('Creating max_proc file...')
        max_proc_file_path = f'{self.base_directory}/Max_Proc.txt'
        with open(max_proc_file_path, 'w') as file:
            file.write(f"{n_cores}\n")

        print(f'Max_Proc.txt file created at: {max_proc_file_path}')

    def create_other_txt_requiered_files(self, pollutant, n_cores) -> None:
        print('Creating other txt requiered files...')
        self.create_pollutant_txt_file(pollutant)
        self.create_percent_file()
        self.create_max_proc_file(n_cores)

    #############################
