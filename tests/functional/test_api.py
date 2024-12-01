import pytest
from tests.conftest import apitest_classfixture


@pytest.mark.usefixtures(apitest_classfixture.__name__)
class TestApiEndpoints:
    """Some functional tests for the API"""

    @pytest.fixture()
    def new_review_response(self):
        """This fixture creates a review and deletes it after the test"""
        # setup
        self.review = {
            "reviewer_name": "Stefan Kecskes",
            "review_title": "Great product",
            "review_rating": 5,
            "review_content": "I really liked this product",
            "email_address": "mr.kecskes@gmail.com",
            "country": "UK",
            "review_date": "2024-12-01"
        }
        response = self.client.post("/reviews", json=self.review)

        # provide
        yield response

        # teardown
        review_id = response.json()["id"]
        self.client.delete(f"/reviews?review_id={review_id}")

    def test_read_root(self):
        # Act
        response = self.client.get("/")

        # Assert
        assert response.status_code == 200
        assert "docs" in str(response.url)

    @pytest.mark.serial
    def test_create_review(self, new_review_response):
        # Assert
        assert new_review_response.status_code == 200
        assert "id" in new_review_response.json()
        assert isinstance(new_review_response.json()["id"], int)

    @pytest.mark.serial
    def test_reviews_by_user(self, new_review_response):
        # Act
        response = self.client.get(f"/reviews_by/{self.review["email_address"]}")

        # Assert
        assert response.status_code == 200
        assert "reviews_by_user" in response.json()
        assert response.json()["reviews_by_user"] == self.review["email_address"]
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["review_title"] == "Great product"
        assert response.json()["data"][0]["review_rating"] == 5

    @pytest.mark.serial
    def test_update_review(self, new_review_response):
        # Arrange
        review_id = new_review_response.json()["id"]
        updated_review = self.review.copy()
        updated_review["review_title"] = "Updated title"
        updated_review["review_rating"] = 4
        updated_review["review_content"] = "Updated content"
        updated_review["id"] = review_id

        # Act
        response = self.client.put("/reviews", json=updated_review)

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == review_id

        updated_review_response =  self.client.get(f"/reviews_by/{self.review["email_address"]}").json()["data"][0]
        assert updated_review_response["review_title"] == updated_review["review_title"]
        assert updated_review_response["review_rating"] == updated_review["review_rating"]
        assert updated_review_response["review_content"] == updated_review["review_content"]

    @pytest.mark.serial
    def test_delete_review(self, new_review_response):
        review_id = new_review_response.json()["id"]
        response = self.client.delete(f"/reviews?review_id={review_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()
        assert response.json()["deleted"] == True
        assert "id" in response.json()
        assert response.json()["id"] == review_id

    @pytest.mark.serial
    def test_reviews(self, new_review_response):
        response = self.client.get("/reviews?records=10&page=1")
        assert response.status_code == 200
        assert "data" in response.json()
        assert len(response.json()["data"]) > 0