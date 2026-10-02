from app.model import PlaceModel

PLACES_DATABASE = {
    "manali": [
        PlaceModel(
            name="Solang Valley",
            description="A beautiful valley known for its adventure sports and scenic views",
            category="Nature",
            rating=4.5,
            estimated_time_hours=4,
        ),
        PlaceModel(
            name="Rohtang Pass",
            description="A high mountain pass offering breathtaking views of the Himalayas",
            category="Nature",
            rating=4.7,
            estimated_time_hours=6,
        ),
        PlaceModel(
            name="Hadimba Temple",
            description="An ancient cave temple surrounded by cedar forests",
            category="Religious Site",
            rating=4.6,
            estimated_time_hours=1,
        ),
    ],
    "goa": [
        PlaceModel(
            name="Baga Beach",
            description="A popular beach in Goa known for its nightlife and water sports",
            category="Beach",
            rating=4.5,
            estimated_time_hours=3,
            entry_fee=None,
        ),
        PlaceModel(
            name="Fort Aguada",
            description="A well-preserved 17th-century Portuguese fort overlooking the Arabian Sea",
            category="Historical Site",
            rating=4.7,
            estimated_time_hours=2,
            entry_fee=10.0,
        ),
        PlaceModel(
            name="Dudhsagar Waterfalls",
            description="A majestic waterfall located on the Mandovi River, surrounded by lush greenery",
            category="Nature",
            rating=4.8,
            estimated_time_hours=5,
            entry_fee=5.0,
        ),
        PlaceModel(
            name="Basilica of Bom Jesus",
            description="A UNESCO World Heritage Site and a famous church in Old Goa",
            category="Religious Site",
            rating=4.6,
            estimated_time_hours=1,
            entry_fee=None,
        ),
    ],
    "jaipur": [
        PlaceModel(
            name="Amber Fort",
            description="A majestic fort located on a hilltop, known for its artistic Hindu style elements",
            category="Historical Site",
            rating=4.7,
            estimated_time_hours=3,
        ),
        PlaceModel(
            name="City Palace",
            description="A beautiful palace complex that showcases a blend of Rajasthani and Mughal architecture",
            category="Historical Site",
            rating=4.5,
            estimated_time_hours=2,
        ),
        PlaceModel(
            name="Hawa Mahal",
            description="A unique five-story palace with a facade resembling a honeycomb, known for its intricate latticework",
            category="Historical Site",
            rating=4.4,
            estimated_time_hours=1,
        ),
        PlaceModel(
            name="Jantar Mantar",
            description="An astronomical observatory with a collection of architectural astronomical instruments",
            category="Historical Site",
            rating=4.3,
            estimated_time_hours=1,
        ),
    ],
}


async def fetch_places(destination: str) -> list[PlaceModel]:
    """Fetch places of interest for a given destination."""
    return PLACES_DATABASE.get(destination.lower(), [])
