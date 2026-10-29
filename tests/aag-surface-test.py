"""Lifecycle regression tests use isolated temporary source and home directories."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]


class SurfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aag-surface-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source with spaces"
        shutil.copytree(SOURCE, self.source,
                        ignore=shutil.ignore_patterns(".git", "state", "__pycache__"))
        self.home = self.root / "home"
        self.home.mkdir()
        self.cwd = self.root / "unrelated working directory"
        self.cwd.mkdir()
        self.entry = self.source / "aag-surface.sh"

    def command(self, *args, success=True):
        self.assertTrue(self.entry.is_file(), "management entry point must exist")
        result = subprocess.run(["sh", str(self.entry), *args], cwd=self.cwd,
                                text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def lifecycle(self, action, **kwargs):
        return self.command(action, "--fixture-home", str(self.home), **kwargs)

    def generated(self):
        return {str(p.relative_to(self.source / "generated")): p.read_bytes()
                for p in (self.source / "generated").rglob("*") if p.is_file()}

    def assert_generated_entries_match_canonical(self):
        canonical = self.source / "canonical"
        output = self.source / "generated"
        rules = {p.stem for p in (canonical / "rules").glob("*.md")}
        self.assertEqual({p.stem for p in (output / "cursor/aag-surface/rules").glob("*.mdc")}, rules)
        for rule in (canonical / "rules").glob("*.md"):
            body = rule.read_text().rstrip() + "\n"
            self.assertIn(body, (output / "codex/AGENTS.md").read_text())
            cursor = output / "cursor/aag-surface/rules" / f"{rule.stem}.mdc"
            self.assertEqual(cursor.read_text().split("---\n", 2)[2], body)
        skills = {p.name for p in (canonical / "skills").iterdir() if p.is_dir()}
        agents = {p.stem for p in (canonical / "agents").glob("*.md")}
        for product, extension in (("codex", "toml"), ("cursor/aag-surface", "md")):
            self.assertEqual({p.parent.name for p in (output / product / "skills").glob("*/SKILL.md")}, skills)
            self.assertEqual({p.stem for p in (output / product / "agents").glob(f"*.{extension}")}, agents)
            for name in skills:
                expected = (canonical / "skills" / name / "SKILL.md").read_text().split("---\n", 2)[2]
                actual = (output / product / "skills" / name / "SKILL.md").read_text().split("---\n", 2)[2]
                self.assertEqual(actual, expected.rstrip() + "\n", f"{product}/skills/{name}/SKILL.md")

    def test_generation_is_reproducible_from_unrelated_directory(self):
        self.command("sync")
        before = self.generated()
        self.command("sync")
        self.assertEqual(before, self.generated())
        self.command("sync", "--check")
        self.command("validate")
        self.assert_generated_entries_match_canonical()
        plugin = json.loads(before["cursor/aag-surface/.cursor-plugin/plugin.json"])
        self.assertEqual(plugin["name"], "aag-surface")

    def test_stale_output_is_detected_without_rewriting(self):
        self.command("sync")
        path = self.source / "generated/codex/AGENTS.md"
        path.write_text("stale\n")
        self.command("sync", "--check", success=False)
        self.command("validate", success=False)
        self.assertEqual(path.read_text(), "stale\n")

    def test_agent_rendering_preserves_access_intent_without_fake_codex_sandbox(self):
        agents = self.source / "canonical/agents"
        agents.mkdir(exist_ok=True)
        (agents / "aag-surface-example.md").write_text(
            '---\nname: aag-surface-example\ndescription: Reviews examples.\n'
            'access: read-only\n---\n# Example\n\nReview the supplied example.\n')
        self.command("sync")
        agent = tomllib.loads((self.source / "generated/codex/agents/aag-surface-example.toml").read_text())
        self.assertEqual(agent["name"], "aag-surface-example")
        self.assertEqual(agent["description"], "Reviews examples.")
        self.assertIn("Do not modify files", agent["developer_instructions"])
        self.assertNotIn("sandbox_mode", agent)
        cursor = (self.source / "generated/cursor/aag-surface/agents/aag-surface-example.md").read_text()
        self.assertIn("readonly: true", cursor)

    def test_invalid_canonical_name_does_not_damage_generated_output(self):
        self.command("sync")
        before = self.generated()
        (self.source / "canonical/rules/unprefixed.md").write_text("# Invalid\n")
        self.command("sync", success=False)
        self.assertEqual(before, self.generated())

    def test_skill_metadata_exports_quoted_strings_for_yaml_significant_text(self):
        skill = self.source / "canonical/skills/aag-surface-author-rule/SKILL.md"
        descriptions = ('Use when comparing options: rules and skills. 😀',
                        'true', 'Use when a # comment marker is literal.')
        for description in descriptions:
            with self.subTest(description=description):
                skill.write_text('---\nname: aag-surface-author-rule\n'
                                 f'description: {description}\n---\n# Author a rule\n\nBody.\n')
                self.command("sync")
                self.command("validate")
                for product in ("codex", "cursor/aag-surface"):
                    output = self.source / "generated" / product / "skills/aag-surface-author-rule/SKILL.md"
                    header = output.read_text().split("---\n")[1]
                    scalar = next(line for line in header.splitlines()
                                  if line.startswith("description: ")).removeprefix("description: ")
                    self.assertTrue(scalar.startswith('"'), "Native YAML metadata must use a quoted string")
                    self.assertEqual(json.loads(scalar), description)
                    self.assertNotIn("\\ud83d", scalar, "YAML cannot represent surrogate escapes")

    def test_agent_toml_accepts_supplementary_unicode_and_control_characters(self):
        agents = self.source / "canonical/agents"
        agents.mkdir(exist_ok=True)
        description = 'Reviews examples: 😀 and DEL \x7f.'
        body = '# Example\n\nReview examples containing 😀 and \x7f.\n'
        (agents / "aag-surface-example.md").write_text(
            '---\nname: aag-surface-example\n'
            f'description: {description}\naccess: inherit\n---\n{body}')
        self.command("sync")
        self.command("validate")
        output = (self.source / "generated/codex/agents/aag-surface-example.toml").read_text()
        try:
            agent = tomllib.loads(output)
        except tomllib.TOMLDecodeError as error:
            self.fail(f"Generated agent must be valid native TOML: {error}")
        self.assertEqual(agent["description"], description)
        self.assertEqual(agent["developer_instructions"], body)

    def test_explicit_invocation_policy_survives_install_and_update(self):
        skill = self.source / "canonical/skills/aag-surface-author-rule/SKILL.md"
        original = skill.read_text()
        skill.write_text(original.replace("\n---\n", "\ninvocation: explicit\n---\n", 1))
        self.command("sync")
        self.lifecycle("install")
        for root in (self.source / "generated/codex", self.home / ".codex",
                     self.source / "generated/cursor/aag-surface",
                     self.home / ".cursor/plugins/local/aag-surface"):
            header = (root / "skills/aag-surface-author-rule/SKILL.md").read_text().split("---\n")[1]
            self.assertIn("disable-model-invocation: true\n", header)
        for root in (self.source / "generated/codex", self.home / ".codex"):
            policy = root / "skills/aag-surface-author-rule/agents/openai.yaml"
            self.assertEqual(policy.read_text(), "policy:\n  allow_implicit_invocation: false\n")
            self.assertFalse((root / "skills/aag-surface-maintain/agents/openai.yaml").exists())
        skill.write_text(original)
        self.command("sync")
        self.lifecycle("install")
        for root in (self.home / ".codex", self.home / ".cursor/plugins/local/aag-surface"):
            self.assertNotIn("disable-model-invocation", (root / "skills/aag-surface-author-rule/SKILL.md").read_text())
            self.assertFalse((root / "skills/aag-surface-author-rule/agents/openai.yaml").exists())

    def test_invalid_or_conflicting_invocation_policy_preserves_output(self):
        skill = self.source / "canonical/skills/aag-surface-author-rule/SKILL.md"
        original = skill.read_text()
        self.command("sync")
        before = self.generated()
        skill.write_text(original.replace("\n---\n", "\ninvocation: typo\n---\n", 1))
        self.command("sync", success=False)
        self.assertEqual(self.generated(), before)
        skill.write_text(original.replace("\n---\n", "\ninvocation: explicit\n---\n", 1))
        policy = skill.parent / "agents/openai.yaml"
        policy.parent.mkdir()
        policy.write_text("policy:\n  allow_implicit_invocation: true\n")
        self.command("sync", success=False)
        self.assertEqual(self.generated(), before)

    def test_install_update_uninstall_preserve_neighbors_and_source(self):
        company = self.home / ".codex/skills/company/SKILL.md"
        company.parent.mkdir(parents=True)
        company.write_text("company skill\n")
        config = self.home / ".codex/config.toml"
        config.write_text('model = "company-default"\n')
        self.command("sync")
        self.lifecycle("install")
        self.lifecycle("install")
        self.assertTrue((self.home / ".codex/AGENTS.md").is_file())
        self.assertTrue((self.home / ".cursor/plugins/local/aag-surface/.cursor-plugin/plugin.json").is_file())
        self.assertFalse(any(p.is_symlink() for p in self.home.rglob("*")))
        self.assertFalse((self.home / ".agents").exists())
        self.assertIn("installed", self.lifecycle("status").stdout)
        rule = self.source / "canonical/rules/aag-surface-workspace-coordination.md"
        rule.write_text(rule.read_text() + "\nRetain the requested evidence.\n")
        self.assertNotIn("Retain the requested evidence", (self.home / ".codex/AGENTS.md").read_text())
        self.command("sync")
        self.lifecycle("install")
        self.assertIn("Retain the requested evidence", (self.home / ".codex/AGENTS.md").read_text())
        self.lifecycle("uninstall")
        self.lifecycle("uninstall")
        self.assertEqual(company.read_text(), "company skill\n")
        self.assertEqual(config.read_text(), 'model = "company-default"\n')
        self.assertTrue((self.home / ".cursor/plugins/local").is_dir())
        self.assertFalse((self.home / ".codex/AGENTS.md").exists())
        self.assertFalse((self.home / ".cursor/plugins/local/aag-surface").exists())
        self.assertTrue(rule.is_file())
        self.assertTrue((self.source / "generated/codex/AGENTS.md").is_file())

    def test_foreign_collision_prevents_all_install_writes(self):
        self.command("sync")
        foreign = self.home / ".codex/AGENTS.md"
        foreign.parent.mkdir()
        foreign.write_text("company guidance\n")
        self.lifecycle("install", success=False)
        self.assertEqual(foreign.read_text(), "company guidance\n")
        self.assertFalse((self.home / ".cursor").exists())
        self.assertFalse((self.source / "state/aag-surface-install.json").exists())

    def test_new_content_and_skill_resources_survive_the_full_lifecycle(self):
        company = self.home / ".codex/skills/company/SKILL.md"
        company.parent.mkdir(parents=True)
        company.write_text("company skill\n")
        self.command("sync")
        self.lifecycle("install")
        original_output = self.generated()

        rule = self.source / "canonical/rules/aag-surface-fixture-guidance.md"
        rule.write_text("# Fixture guidance\n\nReport the requested evidence.\n")
        skill = self.source / "canonical/skills/aag-surface-fixture-resource"
        (skill / "scripts").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: aag-surface-fixture-resource\n"
            "description: Use when reading the fixture resource.\n---\n"
            "# Read the resource\n\nRun `python3 scripts/read-resource.py` from this skill directory.\n")
        resource = skill / "references/message.txt"
        resource.write_text("first resource\n")
        script = skill / "scripts/read-resource.py"
        script.write_text(
            "from pathlib import Path\n"
            "print((Path(__file__).resolve().parents[1] / 'references/message.txt').read_text().strip())\n")
        agent = self.source / "canonical/agents/aag-surface-fixture-review.md"
        agent.parent.mkdir(exist_ok=True)
        agent.write_text(
            "---\nname: aag-surface-fixture-review\ndescription: Reviews fixture evidence.\n"
            "access: read-only\n---\n# Review the fixture\n\nReport the supplied evidence.\n")

        self.command("sync")
        self.command("validate")
        self.assert_generated_entries_match_canonical()
        self.lifecycle("install")
        skill_copies = [self.home / ".codex/skills" / skill.name,
                        self.home / ".cursor/plugins/local/aag-surface/skills" / skill.name]
        cursor_rule = self.home / ".cursor/plugins/local/aag-surface/rules" / f"{rule.stem}.mdc"
        codex_agent = self.home / ".codex/agents" / f"{agent.stem}.toml"
        cursor_agent = self.home / ".cursor/plugins/local/aag-surface/agents" / agent.name

        def assert_installed_version(message, guidance, agent_body):
            self.assertIn(guidance, (self.home / ".codex/AGENTS.md").read_text())
            self.assertIn(guidance, cursor_rule.read_text())
            self.assertIn(agent_body, tomllib.loads(codex_agent.read_text())["developer_instructions"])
            self.assertIn(agent_body, cursor_agent.read_text())
            for installed in skill_copies:
                body = (installed / "SKILL.md").read_text().split("---\n", 2)[2]
                self.assertEqual(body, (skill / "SKILL.md").read_text().split("---\n", 2)[2])
                self.assertEqual((installed / "scripts/read-resource.py").read_bytes(), script.read_bytes())
                self.assertEqual((installed / "references/message.txt").read_text().strip(), message)
                result = subprocess.run(["python3", str(installed / "scripts/read-resource.py")],
                                        cwd=self.cwd, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), message)

        assert_installed_version("first resource", "Report the requested evidence.", "Report the supplied evidence.")
        resource.write_text("updated resource\n")
        rule.write_text("# Fixture guidance\n\nReport updated evidence.\n")
        agent.write_text(agent.read_text().replace("Report the supplied evidence.", "Report updated evidence."))
        self.command("sync")
        assert_installed_version("first resource", "Report the requested evidence.", "Report the supplied evidence.")
        self.lifecycle("install")
        assert_installed_version("updated resource", "Report updated evidence.", "Report updated evidence.")

        rule.unlink()
        shutil.rmtree(skill)
        agent.unlink()
        self.command("sync")
        self.assertEqual(self.generated(), original_output)
        self.lifecycle("install")
        for removed in (*skill_copies, cursor_rule, codex_agent, cursor_agent):
            self.assertFalse(removed.exists(), str(removed))
        installed_roots = {"codex": self.home / ".codex", "cursor": self.home / ".cursor/plugins/local"}
        for relative, expected in original_output.items():
            product, suffix = relative.split("/", 1)
            installed = installed_roots[product] / suffix
            self.assertTrue(installed.is_file(), relative)
            self.assertEqual(installed.read_bytes(), expected, relative)
        self.assertEqual(company.read_text(), "company skill\n")
        self.lifecycle("uninstall")
        self.assertFalse((self.home / ".codex/AGENTS.md").exists())
        self.assertFalse((self.home / ".cursor/plugins/local/aag-surface").exists())
        self.assertEqual(company.read_text(), "company skill\n")
        self.assertEqual(self.generated(), original_output)

    def test_uninstall_works_with_invalid_canonical_content(self):
        company = self.home / ".codex/skills/company/SKILL.md"
        company.parent.mkdir(parents=True)
        company.write_text("company skill\n")
        self.command("sync")
        self.lifecycle("install")
        generated = self.generated()
        invalid = self.source / "canonical/rules/unprefixed.md"
        invalid.write_text("# Invalid name\n\nThis source cannot be generated.\n")
        self.command("validate", success=False)
        self.lifecycle("uninstall")
        self.assertFalse((self.home / ".codex/AGENTS.md").exists())
        self.assertFalse((self.home / ".cursor/plugins/local/aag-surface").exists())
        self.assertEqual(company.read_text(), "company skill\n")
        self.assertEqual(self.generated(), generated)
        self.assertTrue(invalid.is_file())
        self.assertEqual(json.loads(self.lifecycle("status").stdout)["installation"], "not installed")

    def test_symlinked_shared_directory_is_not_followed(self):
        self.command("sync")
        outside = self.root / "outside"
        outside.mkdir()
        (self.home / ".codex").symlink_to(outside, target_is_directory=True)
        self.lifecycle("install", success=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_uninstall_releases_source_binding_before_move(self):
        self.command("sync")
        self.lifecycle("install")
        manifest = self.source / "state/aag-surface-install.json"
        prior = json.loads(manifest.read_text())
        self.lifecycle("uninstall")
        self.assertFalse(manifest.exists())
        # Also release an empty manifest left by an older version.
        manifest.write_text(json.dumps(dict(prior, entries={})))
        self.lifecycle("uninstall")
        self.assertFalse(manifest.exists())
        moved = self.root / "moved source"
        self.source.rename(moved)
        self.source = moved
        self.entry = moved / "aag-surface.sh"
        self.assertEqual(json.loads(self.lifecycle("status").stdout)["installation"], "not installed")
        self.lifecycle("install")
        state = json.loads((moved / "state/aag-surface-install.json").read_text())
        self.assertEqual(state["source"], str(moved))
        self.lifecycle("uninstall")

    def test_removed_skill_is_removed_only_from_owned_entries_on_update(self):
        self.command("sync")
        self.lifecycle("install")
        shutil.rmtree(self.source / "canonical/skills/aag-surface-author-rule")
        self.command("sync")
        self.lifecycle("install")
        self.assertFalse((self.home / ".codex/skills/aag-surface-author-rule").exists())
        self.assertTrue((self.home / ".codex/skills/aag-surface-maintain/SKILL.md").is_file())

    def test_uninstall_rejects_manifest_path_escape(self):
        self.command("sync")
        self.lifecycle("install")
        manifest = self.source / "state/aag-surface-install.json"
        data = json.loads(manifest.read_text())
        data["entries"]["../victim"] = {"kind": "file", "digest": "unused"}
        manifest.write_text(json.dumps(data))
        victim = self.root / "victim"
        victim.write_text("keep\n")
        self.lifecycle("uninstall", success=False)
        self.assertEqual(victim.read_text(), "keep\n")
        self.assertTrue((self.home / ".codex/AGENTS.md").exists())

    def test_transaction_failure_restores_prior_installation(self):
        self.command("sync")
        self.lifecycle("install")
        before = (self.home / ".codex/AGENTS.md").read_bytes()
        state = (self.source / "state/aag-surface-install.json").read_bytes()
        (self.source / "canonical/rules/aag-surface-workspace-coordination.md").write_text("# Changed\n\nChanged guidance.\n")
        self.command("sync")
        spec = importlib.util.spec_from_file_location("surface", self.source / "scripts/aag-surface.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        real_replace = os.replace
        fired = False

        def fail_once(src, dst):
            nonlocal fired
            if str(dst).endswith("aag-surface-install.json") and not fired:
                fired = True
                raise OSError("simulated state write failure")
            return real_replace(src, dst)

        with patch.object(module.os, "replace", fail_once):
            with self.assertRaises(OSError):
                module.install(self.source, self.home)
        self.assertTrue(fired)
        self.assertEqual((self.home / ".codex/AGENTS.md").read_bytes(), before)
        self.assertEqual((self.source / "state/aag-surface-install.json").read_bytes(), state)

    def test_failed_rollback_preserves_backup_for_recovery(self):
        self.command("sync")
        self.lifecycle("install")
        before = (self.home / ".codex/AGENTS.md").read_bytes()
        spec = importlib.util.spec_from_file_location("surface", self.source / "scripts/aag-surface.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        real_replace = os.replace

        def fail_target(src, dst):
            if Path(dst) == self.home / ".codex/AGENTS.md":
                raise OSError("simulated persistent write failure")
            return real_replace(src, dst)

        with patch.object(module.os, "replace", fail_target):
            with self.assertRaises(Exception):
                module.install(self.source, self.home)
        backups = list((self.home / ".codex").glob(".aag-surface-*/old"))
        self.assertTrue(any(p.is_file() and p.read_bytes() == before for p in backups),
                        "a failed rollback must retain the original for manual recovery")

    def test_status_rejects_symlinked_state_directory(self):
        outside = self.root / "outside-state"
        outside.mkdir()
        (self.source / "state").symlink_to(outside, target_is_directory=True)
        self.lifecycle("status", success=False)

    def test_uninstall_without_manifest_preserves_prefixed_foreign_content(self):
        foreign = self.home / ".codex/skills/aag-surface-foreign/SKILL.md"
        foreign.parent.mkdir(parents=True)
        foreign.write_text("owned elsewhere\n")
        self.lifecycle("uninstall")
        self.assertEqual(foreign.read_text(), "owned elsewhere\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
