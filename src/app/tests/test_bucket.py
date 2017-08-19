import unittest
import json
from app import create_app, db


class BucketTestCase(unittest.TestCase):
    """This class represents the bucket test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(env='test')
        self.client = self.app.test_client()
        self.bucket = {'name': 'Go to Borabora for vacation'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def test_bucket_creation(self):
        """Test API can create a bucket (POST request)"""
        res = self.client.post('/buckets/', data=self.bucket)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_all_bucket(self):
        """Test API can get a bucket (GET request)."""
        res = self.client.post('/buckets/', data=self.bucket)
        self.assertEqual(res.status_code, 201)
        res = self.client.get('/buckets/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_bucket_by_id(self):
        """Test API can get a single bucket by using it's id."""
        rv = self.client.post('/buckets/', data=self.bucket)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client.get(
            '/buckets/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Borabora', str(result.data))

    def test_bucket_can_be_edited(self):
        """Test API can edit an existing bucket. (PUT request)"""
        rv = self.client.post(
            '/buckets/',
            data={'name': 'Eat, pray and love'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client.patch(
            '/buckets/1',
            data={
                "name": "Dont just eat, but also pray and love :-)"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client.get('/buckets/1')
        self.assertIn('Dont just eat', str(results.data))

    def test_bucket_deletion(self):
        """Test API can delete an existing bucket. (DELETE request)."""
        rv = self.client.post(
            '/buckets/',
            data={'name': 'Eat, pray and love'})
        self.assertEqual(rv.status_code, 201)
        res = self.client.delete('/buckets/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client.get('/buckets/1')
        self.assertEqual(result.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
