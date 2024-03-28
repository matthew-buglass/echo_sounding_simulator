from trimesh import Trimesh
import matplotlib.pyplot as plt
import cv2
import numpy as np

from utils.geometry import point_in_tri, triangular_plane_intercept
from utils.timing import timed


class CustomTriMesh:
    @timed
    def __init__(self, mesh: Trimesh, field_split=1000):
        """
        A utility wrapper for a Trimesh Object
        Args:
            mesh: A Trimesh object that this utilit class wraps
            field_split: an integer value of how many boxes to split the search field into when looking for points
        """
        print("Instantiating the mesh")
        self.mesh = mesh

        self.search_field = np.empty(shape=(field_split, field_split), dtype=list)
        self.min_x, self.min_y, self.min_z = mesh.bounds[0]
        self.max_x, self.max_y, self.max_z = mesh.bounds[1]

        self.x_bin_size = (self.max_x - self.min_x) / field_split
        self.y_bin_size = (self.max_y - self.min_y) / field_split

        # add the index for the faces that are in a search field bin
        for f, face in enumerate(self.mesh.faces):
            v1 = mesh.vertices[face[0]]
            v2 = mesh.vertices[face[1]]
            v3 = mesh.vertices[face[2]]

            v1_x_idx, v1_y_idx = self._get_bin_indices_(v1[0], v1[1])
            v2_x_idx, v2_y_idx = self._get_bin_indices_(v2[0], v2[1])
            v3_x_idx, v3_y_idx = self._get_bin_indices_(v3[0], v3[1])

            for i in range(min(v1_x_idx, v2_x_idx, v3_x_idx), max(v1_x_idx, v2_x_idx, v3_x_idx) + 1):
                for j in range(min(v1_y_idx, v2_y_idx, v3_y_idx), max(v1_y_idx, v2_y_idx, v3_y_idx) + 1):
                    if self.search_field[i][j] is None:
                        self.search_field[i][j] = [f]
                    else:
                        self.search_field[i][j].append(f)

        # Instantiate the meta-data for building the image representation
        self.original_image = None
        self.current_image = None
        self.image_window_name = "Depth Map"
        self.image_coords = []
        self.drawing = False

        num_pixels = 500
        aspect_ratio = (self.max_x - self.min_x) / (self.max_y - self.min_y)
        self.img_width = int(num_pixels * aspect_ratio)
        self.img_height = int(num_pixels * (1 / aspect_ratio))

        # Create the colour map for our depth map
        self.viridis = np.asarray(plt.get_cmap('viridis').reversed().colors) * 255
        self.viridis = self.viridis.astype(dtype=np.uint8)

    def _get_bin_indices_(self, x, y) -> tuple[int, int]:
        """
        Returns the x and y bin idxs of an x, y point

        Args:
            x: x coordinate (numeric)
            y: y coordinate (numeric)

        Returns:
            (x_idx, y_idx) if the point is within the bounding box of the mesh, None otherwise
        """
        x_idx = int((x - self.min_x) // self.x_bin_size)
        y_idx = int((y - self.min_y) // self.y_bin_size)

        return x_idx, y_idx

    def _image_indices_to_mesh_coordinates(self, x_idx: np.ndarray[int] | int, y_idx: np.ndarray[int] | int) \
            -> tuple[np.ndarray[float], np.ndarray[float]] | tuple[float, float]:
        """
        Converts x and y pixel indices into a real coordinates
        Args:
            x_idx: the width index of an image
            y_idx: the height index of the image

        Returns:
            The real x position value
        """
        x_coords = ((x_idx / self.img_width) * (self.max_x - self.min_x)) + self.min_x
        y_coords = ((y_idx / self.img_height) * (self.max_y - self.min_y)) + self.min_y
        return x_coords, y_coords

    def _mesh_coordinates_to_image_indices(self, x_cord: np.ndarray[float] | float, y_cord: np.ndarray[float] | float) \
            -> tuple[np.ndarray[int], np.ndarray[int]] | tuple[int, int]:
        """
        Converts real x and y coordinates into a pixel indices
        Args:
            x_cord: The real x position value
            y_cord: The real y position value

        Returns:
            The width index of an image
        """
        x_idx = ((x_cord - self.min_x) / (self.max_x - self.min_x)) * self.img_width
        y_idx = ((y_cord - self.min_y) / (self.max_y - self.min_y)) * self.img_height

        x_idx = min(max(0, int(x_idx)), self.img_width - 1)
        y_idx = min(max(0, int(y_idx)), self.img_width - 1)

        return x_idx, y_idx

    def _scale_z_depth_to_colour(self, z_depth):
        """
        Returns a 3 element integer array to represent an RGB colour. Scales according to the Viridis colour map,
        which has been designed to support colour blindness
        https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199239

        Args:
            z_depth: a depth reading

        Returns:
            colour: a 3 element integer array to represent an RGB colour
        """
        # Because of our error pipeline we need to cap this on either end
        colour_idx = max(0, min(int(255 * (z_depth / self.min_z)), len(self.viridis) - 1))
        return self.viridis[colour_idx]

    @timed
    def _build_image_representation(self) -> None:
        """
        Builds an initial top-down image representation of the mesh with a given height and width

        Returns:
            None
        """
        print("Generating top-down image representation")
        self.original_image = np.zeros((self.img_height, self.img_width, 3), dtype=np.uint8)
        grey = np.asarray([159, 159, 159], dtype=np.uint8)
        black = np.asarray([0] * 3, dtype=np.uint8)

        # get actual x and y coordinates
        x_coords, y_coords = self._image_indices_to_mesh_coordinates(
            np.asarray(range(self.img_height)), np.asarray(range(self.img_width))
        )
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                self.original_image[i][j] = grey if self.point_in_mesh(x, y) else black

    def add_depth_reading(self, depth_vector, radius=1) -> None:
        """
        Marks on the image representation a depth reading
        Args:
            depth_vector: a vector of [x y z] coordinates
            radius: and integer of surrounding pixels to also assign the colour to. Put 0 for just the specific pixel/

        Returns:
            None
        """
        x, y, _ = self.original_image.shape
        i, j = self._mesh_coordinates_to_image_indices(depth_vector[0], depth_vector[1])
        colour = self._scale_z_depth_to_colour(depth_vector[2])

        # Add the path to surrounding pixels as well to improve visibility
        for a in range(max(0, i - radius), min(i + radius + 1, x)):
            for b in range(max(0, j - radius), min(j + radius + 1, y)):
                self.original_image[a][b] = colour

    def _show_image_(self) -> None:
        """
        Shows a top-down image representation of an image

        Returns:
            None
        """
        cv2.imshow(self.image_window_name, self.current_image)

    def _process_out_coordinates_(self) -> list[tuple[float, float]]:
        """
        Processes image path coordinates into cartesian coordinates
        Returns:
            A list of start and end points of a path that the ship will take
        """
        # we have to do a transform here because of the differences in image and array indexing
        return [self._image_indices_to_mesh_coordinates(x, y) for y, x in self.image_coords]

    def get_path_over_mesh(self) -> list[tuple[float, float]]:
        """
        Shows a top-down image representation of an image and takes user input to draw a path

        Returns:
            A list of start and end points of a path that the ship will take, if a path was given, and empty list
            otherwise
        """
        if self.original_image is None:
            self._build_image_representation()

        self.current_image = self.original_image.copy()
        self.image_coords = []

        cv2.namedWindow(self.image_window_name)
        cv2.setMouseCallback(self.image_window_name, self._read_mouse_inputs_)
        # record key inputs as long as the window stay open of until q is pressed
        while cv2.getWindowProperty(self.image_window_name, cv2.WND_PROP_VISIBLE) > 0:
            self._show_image_()
            key = cv2.waitKey(1)

            # Close program with keyboard 'q'
            if key == ord('q'):
                cv2.destroyAllWindows()
                return []

        return self._process_out_coordinates_()

    def _read_mouse_inputs_(self, event, x, y, flags, parameters):
        """
        Reads mouse inputs on the mesh image being displayed
        Args:
            event: The event thrown by cv2
            x: the x horizontal of the mouse
            y: the y vertical of the mouse
            flags:
            parameters:

        Returns:

        """
        # Start drawing at mouse down
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            # The ship's path should be a continuous line, so we will reset the path if a user starts drawing again
            self.image_coords = []
            self.current_image = self.original_image.copy()
            self.image_coords.append((x, y))
            print(f"started drawing at {(y, x)}")

        # Draw as the mouse is moved
        elif event == cv2.EVENT_MOUSEMOVE:
            # Draw line
            if len(self.image_coords) > 0:
                if self.drawing:
                    if self.image_coords[-1] != (x, y):
                        self.image_coords.append((x, y))
                        print(f"drawn to {(y, x)}")
                        cv2.line(self.current_image, self.image_coords[-2], self.image_coords[-1], (0, 0, 0), 2)
                        self._show_image_()
        # Stop drawing when the mouse lifts
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.image_coords.append((x, y))
            print(f"stopped drawing at {(y, x)}")

            # Draw line
            cv2.line(self.current_image, self.image_coords[-2], self.image_coords[-1], (0, 0, 0), 2)
            self._show_image_()

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.image_coords = []
            self.current_image = self.original_image.copy()
            self._show_image_()

    def point_in_mesh(self, x, y) -> bool:
        """
        Returns whether a point is within the mesh
        Args:
            x: x coordinate (numeric)
            y: y coordinate (numeric)

        Returns:
            in_mesh: a boolean of whether a point is within the bound of the mesh
        """
        return len(self.find_simplices(x, y)) > 0

    def find_simplices(self, x, y) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Finds the indices of the simplicies that are intercepted by the vertical vector at x, y
        Args:
            x: x coordinate (numeric)
            y: y coordinate (numeric)

        Raises:
            IndexError if x of y are outside the bounds of the mesh's bounding box

        Returns:
            A list of 3-element tuples representing the positions of hte 3 vertices tah make up the
            simplicies that are intercepted by the vertical vector at x, y.
        """
        out_simplices = []
        x_idx, y_idx = self._get_bin_indices_(x, y)

        if x_idx < self.search_field.shape[0] and y_idx < self.search_field.shape[1]:
            faces = self.search_field[x_idx][y_idx]
            if faces is not None:
                for face_idx in self.search_field[x_idx][y_idx]:
                    face = self.mesh.faces[face_idx]
                    v1 = self.mesh.vertices[face[0]]
                    v2 = self.mesh.vertices[face[1]]
                    v3 = self.mesh.vertices[face[2]]

                    if point_in_tri((x, y), v1, v2, v3):
                        out_simplices.append((v1, v2, v3))

        return out_simplices

    def get_shallowest_depth(self, x: float, y: float):
        """
        Provide a tri mesh and an x and y position. Brute force algorithm that returns the shallowest depth
        (what and echo sounder would find)

        Args:
            x: a real x position
            y: a real y position

        Returns:
            z: a real number that is the maximum (shallowest) z position, or None if the specified point is outside the mesh
        """
        max_z = None

        for face in self.find_simplices(x, y):
            v1 = face[0]
            v2 = face[1]
            v3 = face[2]

            z = triangular_plane_intercept(x, y, v1, v2, v3)
            if max_z is None or z > max_z:
                max_z = z

        return max_z

    @property
    def bounds(self):
        return self.mesh.bounds

    @property
    def faces(self):
        return self.mesh.faces

    @property
    def vertices(self):
        return self.mesh.vertices
