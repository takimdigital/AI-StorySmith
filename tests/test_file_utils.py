import unittest
import os
import shutil
from book_generator.file_utils import sanitize_filename, save_to_file, load_from_file

class TestFileUtils(unittest.TestCase):

    def setUp(self):
        self.test_dir = 'test_generated_content'
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename('file*name?'), 'filename')
        self.assertEqual(sanitize_filename('file/name'), 'filename')
        self.assertEqual(sanitize_filename('file:name'), 'filename')

    def test_save_and_load_from_file(self):
        filename = 'test_file.txt'
        content = 'This is a test.'
        save_to_file(self.test_dir, filename, content)
        loaded_content = load_from_file(self.test_dir, filename)
        self.assertEqual(content, loaded_content)

if __name__ == '__main__':
    unittest.main()
