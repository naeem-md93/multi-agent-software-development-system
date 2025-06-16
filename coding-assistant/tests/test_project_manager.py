import os
import unittest
from tempfile import TemporaryDirectory
from coding_assistant import ProjectManager


class TestProjectManager(unittest.TestCase):
    def test_find_project_files(self):
        with TemporaryDirectory() as tmpdir:
            # Create test files and directories
            test_files = [
                "main.py",
                "utils/helper.py",
                "README.md",
                ".git/commit_history.txt",
                "data/sample.txt",
            ]
            
            # Create directory structure
            for path in test_files:
                os.makedirs(os.path.dirname(os.path.join(tmpdir, path)), exist_ok=True)
                with open(os.path.join(tmpdir, path), "w") as f:
                    f.write("# test content")
            
            # Create ProjectManager instance
            pm = ProjectManager(project_path=tmpdir)
            
            # Verify results
            expected_files = [
                os.path.join(tmpdir, "main.py"),
                os.path.join(tmpdir, "utils", "helper.py"),
            ]
            
            # Use set comparison for unordered file lists
            self.assertSetEqual(set(pm.project_files), set(expected_files))
            self.assertEqual(pm.include_extensions, (".py",))
            # Check ignore_dirs contents regardless of order or type
            self.assertSetEqual(set(pm.ignore_dirs), 
                               {".assistant_data", ".idea", ".venv", ".git", ".vscode", "__pycache__"})


    def test_custom_extensions(self):
        with TemporaryDirectory() as tmpdir:
            # Create mixed file types
            files = ["script.py", "notes.txt", "data.csv"]
            for f in files:
                with open(os.path.join(tmpdir, f), "w") as f:
                    f.write("test")
            
            pm = ProjectManager(
                project_path=tmpdir,
                include_extensions=(".txt", ".csv")
            )
            
            # Define expected result
            expected = [
                os.path.join(tmpdir, "notes.txt"),
                os.path.join(tmpdir, "data.csv")
            ]
            
            # Use set comparison to ignore file order
            self.assertSetEqual(set(pm.project_files), set(expected))


    def test_empty_directory(self):
        with TemporaryDirectory() as tmpdir:
            pm = ProjectManager(project_path=tmpdir)
            self.assertEqual(pm.project_files, [])


if __name__ == "__main__":
    unittest.main()
