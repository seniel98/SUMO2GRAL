import pandas as pd


class WeatherDataProcessor:
    """
    A class for processing weather data.

    Methods:
    - retrieve_weather_data(file_name: str) -> pd.DataFrame
    - change_comma_to_dot(df: pd.DataFrame) -> pd.DataFrame
    - rename_df_columns(df: pd.DataFrame) -> pd.DataFrame
    - create_stability_class(df: pd.DataFrame) -> pd.DataFrame
    - create_met_file(df: pd.DataFrame) -> pd.DataFrame
    - process_weather_data(file_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]
    """

    def __init__(self, base_directory):
        """
        Initializes a new instance of the WeatherProcessor class.

        :param base_directory: The base directory where the weather data is stored.
        :type base_directory: str
        """
        self.base_directory = base_directory

    def retrieve_weather_data(self, file_name) -> pd.DataFrame:
        """
        Reads a weather data file and returns a pandas DataFrame with the relevant data.

        Args:
            file_name (str): The name of the weather data file to read.

        Returns:
            pandas.DataFrame: A DataFrame containing the relevant weather data.
        """
        try:
            weather_df = pd.read_csv(f'{self.base_directory}/{file_name}',
                                     sep='\t', skiprows=[0, 1, 2, 4], encoding="ISO-8859-1")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"The file {file_name} could not be found in {self.base_directory}")
        except Exception as e:
            raise e
        return weather_df

    @staticmethod
    def change_comma_to_dot(df: pd.DataFrame) -> pd.DataFrame:
        """
        Replaces commas with dots in specific columns of a pandas DataFrame.

        Args:
        - df: pandas DataFrame

        Returns:
        - df: pandas DataFrame with commas replaced by dots in specific columns
        """
        columns_to_change = ["Veloc.", "Veloc.máx.", "Precip.", "Temp."]
        for column in df.columns:
            if df[column].name in columns_to_change:
                df[column] = df[column].str.replace(",", ".")
                df[column] = df[column].astype(float)
        return df

    @staticmethod
    def rename_df_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Renames the columns of a given DataFrame to match a specific format.

        Args:
            df (pandas.DataFrame): The DataFrame to rename columns for.

        Returns:
            pandas.DataFrame: The DataFrame with renamed columns.
        """
        df.rename(columns={"FECHA": "fecha", "HORA": "hora"}, inplace=True)
        return df

    @staticmethod
    def create_stability_class(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the stability class for each row in the input dataframe based on wind speed and time of day.

        Args:
            df (pd.DataFrame): Input dataframe containing wind speed and time of day data.

        Returns:
            pd.DataFrame: Output dataframe with an additional column "stability_class" containing the stability class for each row.
        """
        # Pasquill stabilitiy classes 1 is very unstable, 7 is very stable
        stabily_class = [1, 2, 3, 4, 5, 6, 7]
        night_hours = ["21:00", "22:00", "23:00", "00:00",
                       "01:00", "02:00", "03:00", "04:00", "05:00", "06:00"]
        # Iterate over all the rows in the dataframe and for each row add the stability class depending on the wind speed and the time of the day (hora)
        for index, row in df.iterrows():
            if row["hora"] not in night_hours:
                if row["Veloc."] < 2:
                    df.loc[index, "stability_class"] = stabily_class[0]
                elif row["Veloc."] >= 2 and row["Veloc."] < 3:
                    df.loc[index, "stability_class"] = stabily_class[1]
                elif row["Veloc."] >= 3 and row["Veloc."] < 5:
                    df.loc[index, "stability_class"] = stabily_class[1]
                elif row["Veloc."] >= 5 and row["Veloc."] < 6:
                    df.loc[index, "stability_class"] = stabily_class[2]
                elif row["Veloc."] >= 6:
                    df.loc[index, "stability_class"] = stabily_class[2]
            else:
                if row["Veloc."] < 2:
                    df.loc[index, "stability_class"] = stabily_class[4]
                elif row["Veloc."] >= 2 and row["Veloc."] < 3:
                    df.loc[index, "stability_class"] = stabily_class[4]
                elif row["Veloc."] >= 3 and row["Veloc."] < 5:
                    df.loc[index, "stability_class"] = stabily_class[5]
                elif row["Veloc."] >= 5 and row["Veloc."] < 6:
                    df.loc[index, "stability_class"] = stabily_class[5]
                elif row["Veloc."] >= 6:
                    df.loc[index, "stability_class"] = stabily_class[5]

        return df

    @staticmethod
    def create_met_file(df: pd.DataFrame) -> pd.DataFrame:
        """
        Removes unnecessary columns from the input DataFrame and returns the updated DataFrame.

        Args:
            df (pandas.DataFrame): The input DataFrame containing weather data.

        Returns:
            pandas.DataFrame: The updated DataFrame with unnecessary columns removed.
        """
        df.drop(columns=['H.Rel.', 'Veloc.máx.', 'Precip.',
                'Temp.', 'R.Sol.', 'Pres.'], inplace=True)
        return df

    def process_weather_data(self, file_name):
        """
        Processes the weather data from the given file name.

        Args:
            file_name (str): The name of the file containing the weather data.

        Returns:
            Tuple: A tuple containing two pandas dataframes. The first dataframe contains the processed weather data, and the second dataframe contains the processed meteorological file data.
        """
        weather_df = self.retrieve_weather_data(file_name)
        weather_df = self.change_comma_to_dot(weather_df)
        weather_df = self.rename_df_columns(weather_df)

        weather_df.dropna(inplace=True)
        weather_df['fecha'] = weather_df['fecha'].str.replace('/', '.')
        weather_df["hora"] = weather_df["hora"].astype(str)+":00"
        weather_df['Direc.'] = weather_df['Direc.'].astype(int)
        weather_df['fecha'] = pd.to_datetime(
            weather_df['fecha'], format='%d.%m.%Y')
        weather_df['hora'] = pd.to_datetime(
            weather_df['hora'], format='%H:%M')
        weather_df.sort_values(by=['fecha', 'hora'], inplace=True)
        weather_df = self.create_stability_class(weather_df)
        weather_df['stability_class'] = weather_df['stability_class'].astype(
            int)

        weather_df['fecha'] = pd.to_datetime(
            weather_df['fecha'], format='%d.%m.%Y').dt.strftime('%d.%m.%Y')
        weather_df['hora'] = pd.to_datetime(
            weather_df['hora'], format='%H:%M').dt.strftime('%H:%M')

        met_file_df = self.create_met_file(weather_df)

        return weather_df, met_file_df

    def write_to_files(self, df, file_name):
        try:
            df.to_csv(f'{self.base_directory}/{file_name}', index=False)
        except Exception as e:
            raise IOError(f"Failed to write to {file_name}: {e}")
