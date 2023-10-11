import obsolete_code.bezier_tools.default as default
import numpy as np

from obsolete_code.bezier_tools.bezier_patch import BezierPatch

class BezierSurface:

    def __init__(self):

        self.patches = []

    def select_all(self):
        for patch in self.patches:
            patch.selected = True

    def deselect_all(self):
        for patch in self.patches:
            patch.selected = False

    def inverset_selection(self):
        for patch in self.patches:
            if patch.selected:
                patch.selected = False
            else:
                patch.selected = True

    def fix_c0_continuity(self):

        """
        This functions averages the edge control points from adjacent patches so that the patches have C0 continuity

        They algorithm may seem a little complex, but what it is doing is quite simple: Find all patches that share
        the same corner-control-point, and where the corner is located on each of them.

        With that information, you can then modify the same corner an all relevant patches

        :return:
        """

        # CORNERS
        for patch in self.patches:

            # Get all patches connected to each of the corners and update their values
            for corner_id in range(4):

                patches_list = self.get_patches_connected_to_corner(starting_patch=patch, starting_corner_id=corner_id)

                # Calculate mean control point from all patches
                cp = np.ndarray((len(patches_list), 3), dtype=np.float32)
                for i, patch_combo in enumerate(patches_list):
                    selected_patch = patch_combo[0]
                    row = patch_combo[1]
                    col = patch_combo[2]
                    cp[i, :] = selected_patch.control_points[row, col, :]
                mean_cp = np.mean(cp, axis=0)

                # Apply mean to all patches
                for patch_combo in patches_list:
                    selected_patch = patch_combo[0]
                    row = patch_combo[1]
                    col = patch_combo[2]
                    selected_patch.control_points[row, col, :] = mean_cp

        # EDGES
        for patch in self.patches:
            for edge_id in default.PATCH_EDGE_LIST:

                adj_patch, adj_patch_edge_id = patch.get_adjacent_patch(edge_id)

                if adj_patch is None:
                    continue

                patch_edge_cp = patch.get_edge_control_points(edge_id=edge_id)
                adj_patch_edge_cp = adj_patch.get_edge_control_points(edge_id=adj_patch_edge_id)

                mean_edge = (patch_edge_cp + np.flip(adj_patch_edge_cp, axis=0)) / 2.0
                adj_patch.set_edge_control_points(edge_id=adj_patch_edge_id,
                                                  edge_control_points=np.flip(mean_edge, axis=0))
                patch.set_edge_control_points(edge_id=edge_id, edge_control_points=mean_edge)

    def get_patches_connected_to_corner(self,
                                        starting_patch,
                                        starting_corner_id,
                                        max_connected_patches=default.MAX_CONNECTED_PATCHES_PER_CORNER):

        # Step 1) Add current patch with corner location to the list
        results_list = []
        row = default.PATCH_CORNER_COORDS[starting_corner_id, 0]
        col = default.PATCH_CORNER_COORDS[starting_corner_id, 1]
        results_list.append([starting_patch, row, col])

        # Step 2) Search all patches connected in CW manner
        test_patch = starting_patch
        test_edge_id = default.CORNER_TO_EDGE_CW[starting_corner_id]
        fully_connected = False

        # First try CW
        for i in range(max_connected_patches - 1):  # It is "-1" because we already add the first patch

            test_patch, adj_patch_edge_id = test_patch.get_adjacent_patch(test_edge_id)

            if test_patch is None:
                break
            if test_patch == starting_patch:
                fully_connected = True
                break

            # Valid patch
            adj_patch_corner_id = default.EDGE_TO_CORNER_CW[adj_patch_edge_id]
            row = default.PATCH_CORNER_COORDS[adj_patch_corner_id, 0]
            col = default.PATCH_CORNER_COORDS[adj_patch_corner_id, 1]
            test_edge_id = default.CORNER_TO_EDGE_CW[adj_patch_corner_id]
            results_list.append([test_patch, row, col])

        # Step 3) Search all patches connected in CW manner of not fully connected
        if not fully_connected:

            test_patch = starting_patch
            test_edge_id = default.CORNER_TO_EDGE_CCW[starting_corner_id]

            for i in range(max_connected_patches - 1):

                test_patch, adj_patch_edge_id = test_patch.get_adjacent_patch(test_edge_id)

                if test_patch == starting_patch:
                    raise Exception('[ERROR] Impossible condition... wtf?!')
                if test_patch is None:
                    break

                # Valid patch
                adj_patch_corner_id = default.EDGE_TO_CORNER_CCW[adj_patch_edge_id]
                row = default.PATCH_CORNER_COORDS[adj_patch_corner_id, 0]
                col = default.PATCH_CORNER_COORDS[adj_patch_corner_id, 1]
                test_edge_id = default.CORNER_TO_EDGE_CCW[adj_patch_corner_id]
                results_list.append([test_patch, row, col])
        return results_list

    def from_regular_patch_network(self, quad_patch_network, enforce_corner_position=False, debug=False):

        """
        This will re-create all the bezier patches from the regular_quad_patches.
        Given that the quad_patches point to each other directly (by reference), "flood-fill" algorithm is used
        to both convert the target patch and its neighbours iteratively

        [WARNING] This function will change the "selected" state of all patches
        :param quad_patch_network: Object from QuadPatchNetwork with network built
        :param enforce_corner_position: If TRUE, the corner positions of the control points will match those
                                        of the quad_patch
        :return:
        """

        if len(quad_patch_network.patches) == 0:
            raise Exception('[ERROR] There are no patches in the regular quad patch network')

        # Step 1)
        #  - Brand all patches with IDs equal to their respective list indices
        #  - Create a respective bezier curve for that patch
        for i, quad_patch in enumerate(quad_patch_network.patches):
            quad_patch.temp_id = i
            new_bezier_patch = BezierPatch()
            new_bezier_patch.from_regular_quad_patch(quad_patch)
            if enforce_corner_position:
                new_bezier_patch.control_points[0, 0, :] = quad_patch.vertices[0, 0, :]
                new_bezier_patch.control_points[0, -1, :] = quad_patch.vertices[0, -1, :]
                new_bezier_patch.control_points[-1, 0, :] = quad_patch.vertices[-1, 0, :]
                new_bezier_patch.control_points[-1, -1, :] = quad_patch.vertices[-1, -1, :]
            self.patches.append(new_bezier_patch)

        # Step 2) Add connectivity information to the bezier patches
        for i, quad_patch in enumerate(quad_patch_network.patches):
            for test_edge_id in default.PATCH_EDGE_LIST:
                adj_quad_patch = quad_patch.adjacent_patches[test_edge_id]
                if adj_quad_patch is not None:
                    self.patches[i].adjacent_patches[test_edge_id] = self.patches[adj_quad_patch.temp_id]

        # Step 3) Clean up all the temp indices from the quad patche
        for i, quad_patch in enumerate(quad_patch_network.patches):
            quad_patch.temp_id = -1

        # ====== [DEBUG] TEST CONNECTIONS =====
        if debug:
            print('[DEBUG] Testing connections')
            for i, patch in enumerate(self.patches):
                print(f'  Patch {i + 1}/{len(self.patches)}')
                for j, edge_id in enumerate(default.PATCH_EDGE_LIST):

                    adj_patch = patch.adjacent_patches[edge_id]
                    if adj_patch is None:
                        print(f'    > No connection')
                        continue
                    else:
                        match = False
                        for k, test_edge_id in enumerate(default.PATCH_EDGE_LIST):
                            reflected_patch = adj_patch.adjacent_patches[test_edge_id]
                            if reflected_patch == patch:
                                match = True  # this edge is the one connected back to the 'patch'
                        if match:
                            print(f'    > OK')
                        else:
                            print(f'    > Wrong')
