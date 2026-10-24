"""The private repository must keep useful security reports without CodeQL upload."""

from pathlib import Path
import unittest

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/security.yml"


class PrivateSecurityWorkflowTests(unittest.TestCase):
    def test_private_repo_skips_code_scanning_uploads_but_keeps_local_scans(self):
        jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
        self.assertIn("github.event.repository.private", jobs["codeql"]["if"])
        self.assertNotIn("if", jobs["secrets"])
        self.assertNotIn("if", jobs["bandit"])

        steps = jobs["bandit"]["steps"]
        scan = next(step for step in steps if step.get("name") == "Run bandit")
        self.assertIn("-f json -o bandit.json", scan["run"])
        artifact = next(step for step in steps if step.get("name") == "Preserve Bandit report")
        self.assertIn("actions/upload-artifact@", artifact["uses"])
        self.assertEqual("bandit.json", artifact["with"]["path"])
        for step in steps:
            if "github/codeql-action/upload-sarif@" in step.get("uses", ""):
                self.assertIn("github.event.repository.private", step["if"])


if __name__ == "__main__":
    unittest.main()
