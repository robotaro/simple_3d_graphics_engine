
GIZMO_3D_RIG_BLUEPRINT = {
    "name": "Gizmo",
    "components": [
        {
            "name": "transform_3d",
            "parameters": {
                "position": "-2 0 2",
                "degrees": "true"
            }
        },
        {
            "name": "gizmo_3d",
            "parameters": {}
        }
    ],
    "entity": [
        {
            "name": "x_axis",
            "components": [
                {
                    "name": "mesh",
                    "parameters": {
                        "shape": "cylinder",
                        "radius": "0.03",
                        "visible": "false",
                        "layer": "1"
                    }
                },
                {
                    "name": "transform_3d",
                    "parameters": {
                        "rotation": "0 0 -90",
                        "degrees": "true"
                    }
                },
                {
                    "name": "material",
                    "parameters": {
                        "diffuse": "red",
                        "shininess_factor": "32.0",
                        "lighting_mode": "solid"
                    }
                }
            ]
        },
        {
            "name": "y_axis",
            "components": [
                {
                    "name": "mesh",
                    "parameters": {
                        "shape": "cylinder",
                        "radius": "0.03",
                        "visible": "false",
                        "layer": "1"
                    }
                },
                {
                    "name": "transform_3d",
                    "parameters": {
                        "rotation": "0 0 0",
                        "degrees": "true"
                    }
                },
                {
                    "name": "material",
                    "parameters": {
                        "diffuse": "green",
                        "shininess_factor": "32.0",
                        "lighting_mode": "solid"
                    }
                }
            ]
        },
        {
            "name": "z_axis",
            "components": [
                {
                    "name": "mesh",
                    "parameters": {
                        "shape": "cylinder",
                        "radius": "0.03",
                        "visible": "false",
                        "layer": "1"
                    }
                },
                {
                    "name": "transform_3d",
                    "parameters": {
                        "rotation": "90 0 0",
                        "degrees": "true"
                    }
                },
                {
                    "name": "material",
                    "parameters": {
                        "diffuse": "blue",
                        "shininess_factor": "32.0",
                        "lighting_mode": "solid"
                    }
                }
            ]
        }
    ]
}