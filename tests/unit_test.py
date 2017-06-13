"""
These unit tests will upload a test file,a test folder and a test contact,
Perform api operations on them,
And them remove them from your account.
"""
from mega import mega
import unittest
import mock
import os
import random

FIND_RESP = None
TEST_CONTACT = 'test@mega.co.nz'
TEST_PUBLIC_URL = 'https://mega.nz/#!1iYHkDTL!rIivzxhmNxHpMzeuua0qPE4_zu9YWz8nhePDUJD6rok'
TEST_FILE = os.path.basename(__file__)
TEST_FOLDER = 'mega.py_testfolder_{0}'.format(random.random())


class TestMega(unittest.TestCase):

    mega = None

    @classmethod
    def setUpClass(cls):
        cls.mega = mega.Mega()
        cls.mega.login()

    def test_mega(self):
        self.assertIsInstance(self.mega, mega.Mega)

    def test_get_user(self):
        resp = self.mega.get_user()
        self.assertIsInstance(resp, dict)

    def test_get_quota(self):
        resp = self.mega.get_quota()
        self.assertIsInstance(int(resp), int)

    def test_get_storage_space(self):
        resp = self.mega.get_storage_space(mega=True)
        self.assertIsInstance(resp, dict)

    def test_get_files(self):
        files = self.mega.get_files()
        self.assertIsInstance(files, dict)

    def test_get_link(self):
        file = self.mega.find(TEST_FILE)
        if file:
            link = self.mega.get_link(file)
            self.assertIsInstance(link, str)

    def test_import_public_url(self):
        resp = self.mega.import_public_url(TEST_PUBLIC_URL)
        file_handle = self.mega.get_id_from_obj(resp)
        resp = self.mega.destroy(file_handle)
        self.assertIsInstance(resp, int)

    def test_create_folder(self):
        resp = self.mega.create_folder(TEST_FOLDER)
        self.assertIsInstance(resp, dict)

    def test_rename(self):
        file = self.mega.find(TEST_FOLDER)
        if file:
            resp = self.mega.rename(file, TEST_FOLDER)
            self.assertIsInstance(resp, int)

    def test_delete_folder(self):
        folder_node = self.mega.find(TEST_FOLDER)[0]
        resp = self.mega.delete(folder_node)
        self.assertIsInstance(resp, int)

    def test_delete(self):
        file = self.mega.find(TEST_FILE)
        if file:
            resp = self.mega.delete(file[0])
            self.assertIsInstance(resp, int)

    def test_destroy(self):
        file = self.mega.find(TEST_FILE)
        if file:
            resp = self.mega.destroy(file[0])
            self.assertIsInstance(resp, int)

    def test_empty_trash(self):
        #resp None if already empty, else int
        resp = self.mega.empty_trash()
        if resp is not None:
            self.assertIsInstance(resp, int)

    def test_add_contact(self):
        resp = self.mega.add_contact(TEST_CONTACT)
        self.assertIsInstance(resp, int)

    def test_remove_contact(self):
        resp = self.mega.remove_contact(TEST_CONTACT)
        self.assertIsInstance(resp, int)

    @mock.patch('requests.post')
    def test_api_request_kwargs(self, m_requests):
        m_requests.return_value.text = '[{}, ""]'
        data = []
        seq_id = self.mega.sequence_num
        response = self.mega._api_request(data, **{'foo': 'bar'})
        self.assertDictEqual({}, response)
        params = {'id': seq_id, 'sid': self.mega.sid, 'foo': 'bar'}
        m_requests.assert_called_once_with('https://g.api.mega.co.nz/cs', data='[]', params=params, timeout=160)

    @mock.patch('requests.post')
    def test_api_request_no_kwargs(self, m_requests):
        m_requests.return_value.text = '[{}, ""]'
        data = []
        seq_id = self.mega.sequence_num
        response = self.mega._api_request(data)
        self.assertDictEqual({}, response)
        params = {'id': seq_id, 'sid': self.mega.sid}
        m_requests.assert_called_once_with('https://g.api.mega.co.nz/cs', data='[]', params=params, timeout=160)


class LoginTests(unittest.TestCase):

    mega = None
    email = None
    password = None

    def setUp(self):
        self.mega = mega.Mega()
        self.email = os.getenv('MEGA_USER')
        self.password = os.getenv('MEGA_PASSWORD')

    def test_login__user(self):
        self.assertIsNone(self.mega.sid)
        self.mega.login(self.email, self.password)
        self.assertIsNotNone(self.mega.sid)

    def test_login__user__request_exception(self):
        self.assertIsNone(self.mega.sid)
        with self.assertRaises(mega.RequestError) as context:
            self.mega.login('test@email.com', 'password')
        self.assertEqual(context.exception.args[0], "Logging error")
        self.assertEqual(context.exception.code, -9)
        self.assertIsNone(self.mega.sid)

    def test_login__anonymous(self):
        self.assertIsNone(self.mega.sid)
        self.mega.login()
        self.assertIsNotNone(self.mega.sid)

    def test_login__anonymous__request_exception(self):
        # TODO: test request exception. Mock api call returning integer value
        pass


class RequestErrorTests(unittest.TestCase):

    def test_exception(self):
        message = 'foo'
        code = -1
        with self.assertRaises(mega.RequestError) as context:
            raise mega.RequestError(message, code)
        self.assertEqual(context.exception.args[0], "foo")
        self.assertEqual(context.exception.code, code)

    def test_exception__no_code(self):
        message = 'foo'
        with self.assertRaises(mega.RequestError) as context:
            raise mega.RequestError(message)
        self.assertEqual(context.exception.args[0], "foo")
        self.assertIsNone(context.exception.code)

if __name__ == '__main__':
    unittest.main()
