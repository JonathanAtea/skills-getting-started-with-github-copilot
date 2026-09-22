import src.app as app_module


class TestActivityRoutes:
    def test_root_redirects_to_frontend(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location

    def test_lists_activities_with_participants(self, client):
        # Arrange
        expected_participants = [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert response.json()["Chess Club"]["participants"] == expected_participants

    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Soccer Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in app_module.activities[activity_name]["participants"]

    def test_duplicate_signup_returns_bad_request(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Student is already signed up for this activity"
        )

    def test_signup_for_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_without_email_returns_unprocessable_entity(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"][-1] == "email"

    def test_remove_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Removed {email} from {activity_name}"
        }
        assert email not in app_module.activities[activity_name]["participants"]

    def test_remove_non_participant_returns_not_found(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "not.registered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Student is not signed up for this activity"
        )

    def test_remove_from_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_activity_state_starts_with_initial_participants(self, client):
        # Arrange
        expected_email = "michael@mergington.edu"

        # Act
        response = client.get("/activities")

        # Assert
        participants = response.json()["Chess Club"]["participants"]
        assert participants == [
            "michael@mergington.edu",
            "daniel@mergington.edu",
        ]
        assert expected_email in participants
