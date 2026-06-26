import ee


def authenticate_gee(project_id):
    print(f"Initializing Google Earth Engine for project: {project_id}...")
    try:
        # Attempt to initialize
        ee.Initialize(project=project_id)
        print("Earth Engine Initialized Successfully. We are in.")
    except Exception as e:
        print(f"Initialization failed: {e}")
        print("Nuking old token and forcing web authentication...")

        # force=True deletes the old cached credentials and forces a new login
        ee.Authenticate(force=True)
        ee.Initialize(project=project_id)
        print("Earth Engine Authenticated and Initialized with new permissions.")


if __name__ == "__main__":
    PROJECT_ID = "isro-urban-heat-ps1"

    authenticate_gee(PROJECT_ID)