from trimesh import Trimesh
# import matplotlib.pyplot as plt
import cv2
import numpy as np

from utils.geometry import point_in_tri, triangular_plane_intercept, get_rotated_vector
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

        num_pixels = 256
        aspect_ratio = (self.max_x - self.min_x) / (self.max_y - self.min_y)
        self.img_width = int(num_pixels * aspect_ratio)
        self.img_height = int(num_pixels * (1 / aspect_ratio))

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

    def _x_image_index_to_coordinate_build(self, x_idx: int) -> float:
        """
        Converts a pixel index into a real x-coordinate
        Args:
            x_idx: the width index of an image

        Returns:
            The real x position value
        """
        return ((x_idx / self.img_width) * (self.max_x - self.min_x)) + self.min_x

    def _y_image_index_to_coordinate_build(self, y_idx: int) -> float:
        """
        Converts a pixel index into a real y-coordinate
        Args:
            y_idx: the height index of an image

        Returns:
            The real y position value
        """
        return ((y_idx / self.img_height) * (self.max_y - self.min_y)) + self.min_y

    def _x_image_index_to_coordinate_display(self, x_idx: int) -> float:
        """
        Converts a pixel index into a real x-coordinate
        Args:
            x_idx: the width index of an image

        Returns:
            The real x position value
        """
        return self._x_image_index_to_coordinate_build(x_idx)

    def _y_image_index_to_coordinate_display(self, y_idx: int) -> float:
        """
        Converts a pixel index into a real y-coordinate
        Args:
            y_idx: the height index of an image

        Returns:
            The real y position value
        """
        # We have to flip the y position, as images index (0,0) in top left,
        # while cartesian normal origin is bottom left
        return (((self.img_height - y_idx) / self.img_height) * (self.max_y - self.min_y)) + self.min_y

    @timed
    def _build_image_representation(self) -> None:
        """
        Builds a top-down image representation of the mesh with a given height and width

        Returns:
            None
        """
        self.image = np.zeros((self.img_height, self.img_width))

        # get actual x and y coordinates
        x_coords = self._x_image_index_to_coordinate_build(np.asarray(range(self.img_height)))
        y_coords = self._y_image_index_to_coordinate_build(np.asarray(range(self.img_width)))
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                rotated_vector = get_rotated_vector(np.asarray([x, y]), -(np.pi / 2))
                self.image[i][j] = self.get_shallowest_depth(rotated_vector[0], rotated_vector[1]) or self.min_z

        # Scale the image
        self.original_image = (
                (self.image - self.image.min()) * (1/(self.image.max() - self.image.min()) * 255)
        ).astype('uint8')

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
        return [
            (self._x_image_index_to_coordinate_display(x), self._y_image_index_to_coordinate_display(y))
            for x, y in self.image_coords
        ]

    def get_path_over_mesh(self) -> list[tuple[float, float]]:
        """
        Shows a top-down image representation of an image

        Returns:
            A list of start and end points of a path that the ship will take
        """
        if self.original_image is None:
            self._build_image_representation()
            self.current_image = self.original_image.copy()

        cv2.namedWindow(self.image_window_name)
        cv2.setMouseCallback(self.image_window_name, self._read_mouse_inputs_)
        # record key inputs as long as the window stay open of until q is pressed
        while cv2.getWindowProperty(self.image_window_name, cv2.WND_PROP_VISIBLE) > 0:
            self._show_image_()
            key = cv2.waitKey(1)

            # Close program with keyboard 'q'
            if key == ord('q'):
                cv2.destroyAllWindows()

        return self._process_out_coordinates_()

    def _read_mouse_inputs_(self, event, x, y, flags, parameters):
        """
        Reads mouse inputs on the mesh image being displayed
        Args:
            event: The event thrown by cv2
            x: the x position of the mouse
            y: the y position of the mouse
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
            print(f"started drawing at {(x, y)}")

        # Draw as the mouse is moved
        elif event == cv2.EVENT_MOUSEMOVE:
            # Draw line
            if len(self.image_coords) > 0:
                if self.drawing:
                    if self.image_coords[-1] != (x, y):
                        self.image_coords.append((x, y))
                        print(f"drawn to {(x, y)}")
                        cv2.line(self.current_image, self.image_coords[-2], self.image_coords[-1], (0, 0, 0), 2)
                        self._show_image_()
        # Stop drawing when the mouse lifts
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.image_coords.append((x, y))
            print(f"stopped drawing at {(x, y)}")

            # Draw line
            cv2.line(self.current_image, self.image_coords[-2], self.image_coords[-1], (0, 0, 0), 2)
            self._show_image_()

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.image_coords = []
            self.current_image = self.original_image.copy()
            self._show_image_()

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
