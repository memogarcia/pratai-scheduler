import unittest
from mock import Mock, patch


class Cluster(unittest.TestCase):
    def setUp(self):
        self.mock_es = Mock()

    def test_announce_ok(self):
        self.mock_es.index.return_value = {'created': True, '_version': 15}
        test_doc = {
            "daemon_type": "daemon_type",
            "daemon_id": "daemon_id",
            "joined_at": "datetime.now()",
            "status": "running"
        }
        res = self.mock_es.index(doc=test_doc)
        self.assertEqual(res, (True, 15))
        self.mock_es.index.assert_called_with(index='pratai',
                                              doc_type='daemon_test',
                                              body=test_doc, id=None)
