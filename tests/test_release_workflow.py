"""Run the workflow's actual release lookup script against mocked GitHub responses."""

import json
from pathlib import Path
import shutil
import subprocess
import textwrap

import pytest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/release.yml"


@pytest.mark.parametrize(
    ("status", "expected"),
    [(200, {"result": True}), (404, {"result": False}),
     (403, {"error": 403}), (500, {"error": 500})],
)
def test_release_lookup(status, expected):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to execute the GitHub Actions script")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    step = workflow.split("      - name: Check existing release\n", 1)[1]
    script = textwrap.dedent(
        step.split("          script: |\n", 1)[1].split("\n      - name:", 1)[0]
    )
    # A tag exists in every scenario. Only the release API response should matter.
    harness = """
const assert = require('node:assert/strict');
const context = {repo: {owner: 'owner', repo: 'repo'}};
process.env.RELEASE_TAG = 'v0.3.0';
const github = {rest: {repos: {getReleaseByTag: async (args) => {
  assert.deepEqual(args, {...context.repo, tag: 'v0.3.0'});
  if (STATUS !== 200) throw Object.assign(new Error('API error'), {status: STATUS});
  return {data: {tag_name: 'v0.3.0'}};
}}}};
(async () => {
  try {
    const result = await (async () => { SCRIPT })();
    console.log(JSON.stringify({result}));
  } catch (error) {
    console.log(JSON.stringify({error: error.status}));
  }
})();
""".replace("STATUS", str(status)).replace("SCRIPT", script)
    result = subprocess.run(
        [node, "-e", harness], check=True, capture_output=True, text=True
    )
    assert json.loads(result.stdout) == expected


def test_release_creation_uses_release_lookup_not_tag_lookup():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "steps.release_exists.outputs.result == 'false'" in workflow
    assert "steps.release_exists.outputs.result == 'true'" in workflow
    assert "tag_exists" not in workflow
    assert "git rev-parse" not in workflow
