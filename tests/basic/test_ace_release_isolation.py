import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class TestAceReleaseIsolation(unittest.TestCase):
    def test_all_inherited_jobs_are_upstream_only(self):
        for path in (ROOT / ".github/workflows").glob("*.yml"):
            if path.name == "ace-candidate-release.yml":
                continue
            lines = path.read_text().splitlines()
            jobs = False
            for index, line in enumerate(lines):
                if line == "jobs:":
                    jobs = True
                    continue
                if jobs and line.startswith("  ") and not line.startswith("   ") and line.endswith(":"):
                    self.assertEqual(
                        lines[index + 1], "    if: github.repository == 'Aider-AI/aider'", path
                    )

    def test_fork_distribution_does_not_claim_official_package_or_command(self):
        text = (ROOT / "pyproject.toml").read_text()
        self.assertIn('name = "acedatacloud-aider"', text)
        self.assertNotIn('name = "aider-chat"', text)
        self.assertIn('ace-aider = "aider.main:main"', text)
        self.assertNotIn('\naider = "aider.main:main"', text)
        self.assertIn('include = ["aider", "aider.*"]', text)

    def test_candidate_workflow_never_uploads_to_registry(self):
        text = (ROOT / ".github/workflows/ace-candidate-release.yml").read_text()
        self.assertIn("github.repository == 'AceDataCloud/Aider'", text)
        for forbidden in ("twine upload", "docker/login", "push: true", "deploy-pages"):
            self.assertNotIn(forbidden, text)

    def test_build_script_can_be_imported_without_side_effects(self):
        spec = importlib.util.spec_from_file_location("ace_release", ROOT / "scripts/build_ace_release.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))


if __name__ == "__main__":
    unittest.main()
