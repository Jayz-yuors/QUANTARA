import osmnx as ox
import matplotlib.pyplot as plt


def extract_urban_infrastructure(lat, lon, dist_meters):
    print(f"Fetching building data for coordinates: {lat}, {lon}...")

    # Define the coordinates (Thane West, Vrindavan Society area)
    location_point = (lat, lon)

    # Configure osmnx to use a local cache to speed up repeated runs
    ox.settings.use_cache = True
    ox.settings.log_console = True

    try:
        # Fetch building footprints within the specified radius
        tags = {'building': True}
        buildings = ox.features_from_point(location_point, tags=tags, dist=dist_meters)

        print(f"Successfully extracted {len(buildings)} buildings.")

        # Plot the data
        fig, ax = ox.plot_footprints(buildings, filepath='thane_buildings.png',
                                     save=True, show=True, color='red')
        print("Map saved as 'thane_buildings.png'.")

    except Exception as e:
        print(f"Data extraction failed: {e}")


if __name__ == "__main__":
    # Coordinates for Thane West
    LATITUDE = 19.2045
    LONGITUDE = 72.9749
    RADIUS = 2000  # 2 kilometers

    extract_urban_infrastructure(LATITUDE, LONGITUDE, RADIUS)