import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import json

# Loading skill scripts must not leave __pycache__ in the canonical skill
# directory; the generator treats it as a resource and validate reports stale output.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1] / 'canonical/skills/aag-surface-onboard-repository'
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class OnboardingTests(unittest.TestCase):
    def test_jsonc(self):
        parser = load('validate_jsonc')
        self.assertEqual(parser.loads('{/*comment*/"url":"https://x", "a":[1,],}'), {'url':'https://x', 'a':[1]})
        self.assertEqual(parser.loads('{"x":"a\\\"//b"}'), {'x':'a"//b'})
        for text in ['{/* unterminated', '{"a":}', '{"a":NaN}', '{"a":1,,}']:
            with self.assertRaises(ValueError): parser.loads(text)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'settings.json'
            path.write_text('{// note\n"a":1,}')
            before = path.read_bytes()
            self.assertEqual(parser.main([str(path)]), 0)
            self.assertEqual(path.read_bytes(), before)

    def test_core_and_unknown(self):
        scopes = load('setting_scopes')
        with patch.object(scopes, 'manifest_paths', return_value=[]) as discovery:
            self.assertEqual(scopes.main(['editor.defaultFormatter'], 'code'), 0)
            discovery.assert_called_with('code', None)
            self.assertEqual(scopes.main(['unknown.setting'], 'cursor'), 1)

    def test_conflict(self):
        scopes = load('setting_scopes')
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name, scope in [('one','resource'), ('two','window')]:
                path = Path(tmp)/f'{name}.json'
                path.write_text(json.dumps({'name':name,'publisher':'test','contributes':{'configuration':{'properties':{'test.key':{'scope':scope}}}}}))
                paths.append(str(path))
            with patch.object(scopes,'manifest_paths', return_value=paths):
                self.assertEqual(scopes.main(['test.key'], 'cursor'),1)

    def test_selected_editor_and_version(self):
        scopes = load('setting_scopes')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exe = root/'bin/code'; exe.parent.mkdir(); exe.touch()
            (root/'resources/app/extensions').mkdir(parents=True)
            extension = root/'selected'; extension.mkdir()
            (extension/'package.json').write_text('{"version":"2"}')
            def run(command, **kwargs):
                self.assertEqual(command[0], str(exe))
                from subprocess import CompletedProcess
                return CompletedProcess(command,0,'test.ext@2\n' if '--list-extensions' in command else str(extension),'')
            with patch.object(scopes.shutil,'which',return_value=str(exe)), patch.object(scopes.subprocess,'run', side_effect=run):
                self.assertEqual(scopes.manifest_paths('code'),[str(extension/'package.json')])
                (extension/'package.json').write_text('{"version":"1"}')
                with self.assertRaises(ValueError): scopes.manifest_paths('code')

if __name__ == '__main__': unittest.main(verbosity=2)
