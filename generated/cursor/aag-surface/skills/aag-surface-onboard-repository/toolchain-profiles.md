# Toolchain profiles

Reference for step 3 of `SKILL.md`. Each profile lists where to read the
evidence and which settings are candidates. A candidate becomes a setting only
when the repository's own files show the tool is used, the key exists in an
installed extension (`python3 setting_scopes.py --editor <cursor|code> <key>`), and its scope permits
folder settings. A repository can match several profiles; combine them.

Every profile answers the same five questions:

1. **Runtime** – which interpreter, SDK, or runtime version the project pins,
   and the persistent location it is installed to.
2. **Task runner** – the command CI runs (`tox run -e lint`, `npm run lint`,
   `dotnet build`, `make lint`), which names the tools and their order.
3. **Pinned tools** – where the project-local copies of formatter, linter, and
   type checker live, and the lockfile that pins their versions.
4. **Module roots and excluded trees** – directories the task runner adds to
   the import/module path, and vendored or generated trees to keep resolvable
   but free of diagnostics.
5. **Editor-only checkers** – anything the editor would report that CI does
   not run; turn it off for the folder or, when window-scoped, note it.

## Python

- Detection: `pyproject.toml`, `tox.ini`, `setup.cfg`, `requirements*.txt`,
  `uv.lock`, `poetry.lock`.
- Runtime: `requires-python`, `.python-version`, tox `base_python`. Install
  with `uv python install <X.Y>`; locate with `uv python find --system <X.Y>`
  (without `--system`, uv returns a project `.venv` when run inside a repo).
- Task runner: tox environments in `tox.ini`; read `[testenv] set_env
  PYTHONPATH` and each `[testenv:<name>]` `commands`. CI workflow usually runs
  `tox run -e lint` and `tox run -e unit`.
- Create an environment without running its suite, from the repository root:

  ```sh
  PY="$(uv python find --system <X.Y>)"
  tox run -e <env> --notest -x "testenv:<env>.basepython=$PY"
  ```

  Inspect resolved tox configuration before setup. `--notest` skips pre/main/post commands. If dependencies are installed in `commands_pre`, run only the inspected dependency command using `tox exec -e <env> -- <dependency-command>` (for example the exact Poetry install groups). Never replay whole hooks. Inspect package installation hooks for effects outside the allowed scope.

  Poetry installs can time out when several build in parallel; set
  `POETRY_REQUESTS_TIMEOUT=300` and rerun failed environments one at a time.
- Candidate keys:
  - `python.defaultInterpreterPath` – the tox environment whose install
    includes pytest (`unit`, or `smoke` where there is no `unit`).
  - `ruff.path` – `["${workspaceFolder}/.tox/lint/bin/ruff"]` when lint runs
    Ruff. Resource-scoped, so each root keeps its own pin.
  - `cursorpyright.analysis.extraPaths` – the `PYTHONPATH` entries relative to
    `{tox_root}`, excluding the root itself (charms: `["src", "lib"]`; a package
    that sits in the root needs none).
  - `cursorpyright.analysis.ignore` – vendored trees the repository's lint
    excludes (`["lib"]`, `["<package>/lib"]`).
- Window-only: `ty.path`, `ty.diagnosticMode`. Pyright's own
  `typeCheckingMode` is kept `off` at window level because CI type-checks
  with ty; Pyright diagnostics would be visible only locally.
- Verify: `test -e .tox/<env>/bin/python`, `.tox/lint/bin/ruff version`,
  `.tox/lint/bin/ty version` against the lockfile.

## Node.js / TypeScript

- Detection: `package.json`, `package-lock.json`, `pnpm-lock.yaml`,
  `yarn.lock`, `bun.lockb`, `tsconfig*.json`, `.nvmrc`, `.node-version`.
- Runtime: `engines.node`, `.nvmrc`, `.node-version`, `.tool-versions`,
  `volta` field in `package.json`. Install with the user's version manager
  (`nvm`, `fnm`, `volta`, `mise`) and report which; do not point settings at a
  version-manager shim that changes with the shell's current version.
- Task runner: `package.json` `scripts` (`lint`, `format`, `typecheck`,
  `test`) and the CI workflow's `npm run`/`pnpm`/`yarn` lines. The lockfile
  present decides the package manager.
- Pinned tools: `node_modules/.bin/{eslint,prettier,tsc,biome,vitest,jest}`
  after `<pm> install --frozen-lockfile` (`npm ci`). Versions in the lockfile.
- Module roots: `tsconfig.json` `paths`/`baseUrl` are read by the TypeScript
  server directly; no editor setting is needed. Exclude `dist/`, `build/`,
  `coverage/`, generated clients from diagnostics with the tool's own config,
  not editor settings.
- Candidate keys (confirm each with `setting_scopes.py`):
  - `npm.packageManager` – `npm`, `pnpm`, `yarn`, or `bun` as the lockfile
    says.
  - `eslint.enable` – `false` when the repository does not run ESLint (for
    example Biome-only). `eslint.workingDirectories` with `{"mode": "auto"}`
    or explicit subpaths for monorepos. ESLint resolves the local
    `node_modules` copy itself; set `eslint.nodePath` only when CI uses a
    different install location.
  - `prettier.prettierPath` – only when the extension does not already pick
    up the local `node_modules/prettier`; usually unnecessary.
  - `biome.lsp.bin` – the local Biome binary when Biome is the linter.
  - `editor.defaultFormatter` per language (`[typescript]`, `[json]`) to
    match the formatter CI runs; leave unset when the repository runs none.
  - `deno.enable` – `true` only for Deno projects, `false` where the Deno
    extension is installed but the repository is Node.
- Window-only: `typescript.tsdk` (the workspace TypeScript version). In a
  multi-root window it can name one `node_modules/typescript/lib`; if roots
  pin different TypeScript versions, report the conflict and leave it unset
  so the bundled TypeScript is used for navigation, with `tsc` from
  `node_modules/.bin` as the authoritative check.
- Verify: `node --version` against the pin, `node_modules/.bin/<tool>
  --version` against the lockfile, inspect `package.json` scripts without executing them. `npm run lint --dry-run` executes lint and must not be used.

## .NET

- Detection: `*.sln`, `*.slnx`, `*.csproj`, `*.fsproj`, `global.json`,
  `Directory.Build.props`, `.editorconfig` with `dotnet_*` rules.
- Runtime: `global.json` `sdk.version` and `rollForward`; otherwise the
  highest `TargetFramework`. Install with `dotnet-install.sh` or the system
  package and report; check with `dotnet --list-sdks`.
- Task runner: `dotnet restore`, `dotnet build`, `dotnet format
  --verify-no-changes`, `dotnet test`, as the CI workflow orders them.
  Analyzers and `TreatWarningsAsErrors` come from the project files.
- Pinned tools: `.config/dotnet-tools.json` local tools, restored with
  `dotnet tool restore`. Formatting rules live in `.editorconfig`, which the
  C# language server reads directly.
- Module roots: project references; no editor setting.
- Candidate keys (confirm each with `setting_scopes.py`; they belong to the
  C# / C# Dev Kit extensions, which may not be installed):
  - `dotnet.defaultSolution` – the solution file to open when the repository
    has more than one.
  - `dotnet.preferCSharpExtension` / `dotnet.server.useOmnisharp` – only to
    match a repository that documents OmniSharp.
  - `omnisharp.enableRoslynAnalyzers`, `omnisharp.enableEditorConfigSupport`
    – only for the OmniSharp path.
- Editor-only checkers: analyzers the editor enables that the project files
  do not; keep the project's `.editorconfig` as the single source.
- Verify: `dotnet --version` resolves under `global.json`, `dotnet tool
  list` shows restored tools, inspect the default solution and project configuration without building.

## Go

- Detection: `go.mod`, `go.work`, `.golangci.yml`.
- Runtime: `go` directive and `toolchain` line in `go.mod`; `go version`.
- Task runner: `go build ./...`, `go vet ./...`, `golangci-lint run`,
  `go test ./...`, per the CI workflow or `Makefile`.
- Pinned tools: `golangci-lint` version from the CI action or
  `.golangci.yml`; install to a persistent location (`$GOBIN` or `~/go/bin`).
- Candidate keys: `go.lintTool` and `go.lintFlags` to match CI,
  `go.alternateTools` to name a pinned `golangci-lint`, `gopls` `build.directoryFilters`
  for vendored or generated trees. `go.goroot` only when the module pins a
  toolchain the default `go` is not.
- Verify: `go version`, `golangci-lint --version`, inspect configured check commands without executing them.

## Rust

- Detection: `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`,
  `clippy.toml`, `rustfmt.toml`.
- Runtime: `rust-toolchain.toml` channel and components; `rustup` installs
  it on first use.
- Task runner: `cargo fmt --check`, `cargo clippy -- -D warnings`,
  `cargo test`, per CI.
- Candidate keys: `rust-analyzer.check.command` set to `clippy` when CI runs
  clippy, `rust-analyzer.cargo.features` to match CI's feature set,
  `rust-analyzer.linkedProjects` for a workspace whose `Cargo.toml` is not at
  the root.
- Verify: `cargo --version`, `cargo clippy --version`, matching
  `rust-toolchain.toml`.

## Shell, YAML, Markdown, and documentation repositories

- Detection: `Makefile`, `.yamllint`, `.vale.ini`, `.markdownlint*`,
  `conf.py`, `mkdocs.yml`, `snap/snapcraft.yaml`, `rockcraft.yaml`.
- Task runner: `Makefile` targets or tox environments that run `yamllint`,
  `shellcheck`, `vale`, `markdownlint`, `sphinx-build`.
- Candidate keys: `yaml.schemas` only when the repository documents a
  schema; `shellcheck.executablePath` when the ShellCheck extension is
  installed and CI pins a version. Formatting-on-save settings that would
  rewrite documentation (trailing whitespace in Markdown hard breaks) are
  reported, not changed, because they are user-level.
- A repository with none of these tools gets no `.vscode/settings.json`.

## Unknown stack

Do not guess. Record the detection files found, the CI commands, and the
tools they call. Propose settings only for keys whose extension is installed
and whose purpose is evident from the repository's own configuration. Report
the stack as unprofiled so this file can be extended.
