import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from urllib.request import Request, urlopen
import io
from PIL import Image
import pyproj


class MapGenerator:
    """
    A class for generating georeferenced maps using Cartopy and saving them as PNG files with corresponding .pgw files.
    """

    def __init__(self, base_directory):
        """
        Initializes a MapGenerator object.

        Args:
            base_directory (str): The base directory where the generated maps will be saved.
        """
        self.base_directory = base_directory

    def create_georeferenced_map(self, location, epsg, filename):
        """
        Creates a georeferenced map using Cartopy and saves it as a PNG file with a corresponding .pgw file.

        Args:
            location (dict): A dictionary containing the geographic coordinates of the map's bounding box.
                The dictionary should have the following keys:
                - north: float, the northernmost latitude of the bounding box
                - south: float, the southernmost latitude of the bounding box
                - east: float, the easternmost longitude of the bounding box
                - west: float, the westernmost longitude of the bounding box
            epsg (str): The EPSG code of the coordinate reference system of the map.
            filename (str): The name of the map file.

        Returns:
            None
        """
        print("Creating georeferenced map...")

        # Plot using Cartopy
        fig, ax = plt.subplots(
            subplot_kw={'projection': ccrs.epsg(f'{epsg}')})
        ax.set_extent([location["west"], location["east"],
                       location["south"], location["north"]], crs=ccrs.epsg(f'{epsg}'))

        # Add OSM image as background
        osm_img = cimgt.OSM()
        zoom = 16    # Adjust this value to suit your needs
        ax.add_image(osm_img, zoom)

        # Save to PNG
        output_filename = f'{self.base_directory}/{filename}_epsg{epsg}.png'
        plt.savefig(output_filename, dpi=300, bbox_inches='tight',
                    pad_inches=0)  # Adjust for tight layout
        plt.close()

        # Read the image
        im = Image.open(output_filename)
        width_of_png_image = im.width
        height_of_png_image = im.height
        resolution_x = (location["east"] -
                        location["west"]) / width_of_png_image
        resolution_y = (location["south"] -
                        location["north"]) / height_of_png_image

        # Generate .pgw file
        pgw_filename = output_filename.replace('.png', '.pngw')
        with open(pgw_filename, 'w') as f:
            f.write(str(resolution_x) + "\n")
            f.write("0.0\n")  # No rotation in y
            f.write("0.0\n")  # No rotation in x
            # Resolution in y, negative because the y-axis is flipped in image coordinates
            f.write(str(resolution_y) + "\n")
            f.write(str(location['west']) + "\n")  # X pos
            f.write(str(location['north']) + "\n")  # Y pos

        print(
            f"Map saved as {output_filename} with corresponding {pgw_filename}")

    def generate_map(self, location, epsg, directory, filename):
        """
        Generates a georeferenced map using Cartopy and saves it as a PNG file with a corresponding .pgw file.

        Args:
            location (dict): A dictionary containing the geographic coordinates of the map's bounding box.
                The dictionary should have the following keys:
                - north: float, the northernmost latitude of the bounding box
                - south: float, the southernmost latitude of the bounding box
                - east: float, the easternmost longitude of the bounding box
                - west: float, the westernmost longitude of the bounding box
            epsg (str): The EPSG code of the coordinate reference system of the map.
            directory (str): The directory where the map will be saved.
            filename (str): The name of the map file.

        Returns:
            None
        """
        cimgt.OSM.get_image = image_spoof
        self.create_georeferenced_map(location, epsg, directory, filename)

    @staticmethod
    def convert_coordinates(x, y, src_crs, dst_crs):
        """
        Convert x, y coordinates from src_crs to dst_crs using pyproj.

        Parameters:
        - x, y: Arrays or lists of x and y coordinates.
        - src_crs: Source coordinate reference system (EPSG code).
        - dst_crs: Target coordinate reference system (EPSG code).

        Returns:
        - x_out, y_out: Arrays of transformed x and y coordinates.
        """
        try:
            transformer = pyproj.Transformer.from_crs("EPSG:{}".format(
                src_crs), "EPSG:{}".format(dst_crs), always_xy=True)
            x_out, y_out = transformer.transform(x, y)
            return x_out, y_out
        except Exception as e:
            print(f"{e}")
            return None, None
        


def image_spoof(self, tile):
    url = self._image_url(tile)  # get the url of the street map API
    req = Request(url)  # start request
    req.add_header('User-agent', 'Anaconda 3')  # add user agent to request
    fh = urlopen(req)
    im_data = io.BytesIO(fh.read())  # get image
    fh.close()  # close url
    img = Image.open(im_data)  # open image with PIL
    img = img.convert(self.desired_tile_form)  # set image format
    return img, self.tileextent(tile), 'lower'  # reformat for cartopy
