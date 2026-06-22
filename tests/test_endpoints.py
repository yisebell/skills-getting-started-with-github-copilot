import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_all_activities_returns_success(self, client):
        # Arrange: client is ready (from fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self, client):
        # Arrange: client is ready
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess
        assert isinstance(chess["participants"], list)


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_succeeds(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        
        # Verify in activities list
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]

    def test_signup_already_registered_returns_error(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_multiple_students_same_activity(self, client):
        # Arrange
        activity_name = "Programming Class"
        emails = ["alice@mergington.edu", "bob@mergington.edu"]
        
        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify both are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()["Programming Class"]["participants"]
        for email in emails:
            assert email in participants


class TestRemove:
    """Test POST /activities/{activity_name}/remove endpoint"""
    
    def test_remove_participant_succeeds(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        
        # Verify removed from activities list
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]

    def test_remove_nonexistent_participant_returns_error(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_remove_then_signup_same_student(self, client):
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        
        # Act: Remove student
        remove_response = client.post(
            f"/activities/{activity_name}/remove?email={email}"
        )
        
        # Assert removal succeeded
        assert remove_response.status_code == 200
        
        # Act: Sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert signup succeeded
        assert signup_response.status_code == 200
        
        # Verify re-registered
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Gym Class"]["participants"]
