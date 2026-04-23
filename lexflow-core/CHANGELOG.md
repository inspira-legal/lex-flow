# CHANGELOG

<!-- version list -->

## v1.18.0 (2026-04-23)

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`07280de`](https://github.com/inspira-legal/lex-flow/commit/07280def975f58d3dbe273185be660a59a2b3e2b))

### Features

- **core**: Add Google Drive opcodes
  ([`fd61a84`](https://github.com/inspira-legal/lex-flow/commit/fd61a846a93fd5ec99aac47458455d119c19381d))


## v1.17.0 (2026-03-30)

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`3a99a4e`](https://github.com/inspira-legal/lex-flow/commit/3a99a4e1b8b7d2b0cd097143b51b4a1e09d0b0ec))

### Features

- **core**: Add http_post_json and http_post_data opcodes
  ([`9f37ec8`](https://github.com/inspira-legal/lex-flow/commit/9f37ec8dd17ef1ab0c4e6ee191def5ad030ffdea))


## v1.16.0 (2026-03-25)

### Bug Fixes

- **core**: Add dependency checks, ID validation, and missing tests for Clicksign/ReceitaWS opcodes
  ([#57](https://github.com/inspira-legal/lex-flow/pull/57),
  [`427ef5b`](https://github.com/inspira-legal/lex-flow/commit/427ef5bdad108e0d0d46f328a1f657952e442fad))

- **core**: Add HTTP timeouts, input validation and error path tests for Clicksign/ReceitaWS opcodes
  ([#57](https://github.com/inspira-legal/lex-flow/pull/57),
  [`427ef5b`](https://github.com/inspira-legal/lex-flow/commit/427ef5bdad108e0d0d46f328a1f657952e442fad))

### Documentation

- Regenerate opcode reference after merge ([#57](https://github.com/inspira-legal/lex-flow/pull/57),
  [`427ef5b`](https://github.com/inspira-legal/lex-flow/commit/427ef5bdad108e0d0d46f328a1f657952e442fad))

### Features

- **opcode**: Add Clicksign v3 and ReceitaWS opcodes
  ([#57](https://github.com/inspira-legal/lex-flow/pull/57),
  [`427ef5b`](https://github.com/inspira-legal/lex-flow/commit/427ef5bdad108e0d0d46f328a1f657952e442fad))

- **workflow**: Enhance contrato_envio workflow with detailed logging and error handling
  ([#57](https://github.com/inspira-legal/lex-flow/pull/57),
  [`427ef5b`](https://github.com/inspira-legal/lex-flow/commit/427ef5bdad108e0d0d46f328a1f657952e442fad))


## v1.15.1 (2026-03-24)

### Bug Fixes

- **core**: Allow pydantic-ai-slim >=1.0
  ([`2599a46`](https://github.com/inspira-legal/lex-flow/commit/2599a4660a2583914681290f4dadeff41cc01ccc))

- **core**: Update dependency lock file for pydantic-ai-slim >=1.0
  ([`bafc0c7`](https://github.com/inspira-legal/lex-flow/commit/bafc0c7d7672938fad1d2ba04f7392f6f92bb786))

### Chores

- **cli**: Release 1.6.0
  ([`e449a89`](https://github.com/inspira-legal/lex-flow/commit/e449a8926feb116a218b740d19eabff95bdedd32))

- **core**: Bump pydantic-ai-slim to >=1.0
  ([`ee70e2e`](https://github.com/inspira-legal/lex-flow/commit/ee70e2ea53965a820351c86313054489772accf7))

- **web**: Build frontend library [skip ci]
  ([`64abc91`](https://github.com/inspira-legal/lex-flow/commit/64abc91683f1a665a95ce283242c788bd0de06e7))

- **web**: Release 1.15.0
  ([`27d6ce6`](https://github.com/inspira-legal/lex-flow/commit/27d6ce63d901cc0e02bedeb51b2d85e53b792520))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`44216e4`](https://github.com/inspira-legal/lex-flow/commit/44216e47422c0161501f0eaaa2ed58f9eab199cf))


## v1.15.0 (2026-03-17)

### Bug Fixes

- Correct API usage in lex-flow-builder skill
  ([#44](https://github.com/inspira-legal/lex-flow/pull/44),
  [`b381c23`](https://github.com/inspira-legal/lex-flow/commit/b381c23107f7b6a0d69116b994f9d11c6dc16ea8))

- Correct reference.md with official YAML structure and opcodes
  ([#44](https://github.com/inspira-legal/lex-flow/pull/44),
  [`b381c23`](https://github.com/inspira-legal/lex-flow/commit/b381c23107f7b6a0d69116b994f9d11c6dc16ea8))

- Rename to SKILL.md and align with best practices
  ([#44](https://github.com/inspira-legal/lex-flow/pull/44),
  [`b381c23`](https://github.com/inspira-legal/lex-flow/commit/b381c23107f7b6a0d69116b994f9d11c6dc16ea8))

- **opcodes**: Address review feedback on Apollo opcodes
  ([#51](https://github.com/inspira-legal/lex-flow/pull/51),
  [`c9ac55e`](https://github.com/inspira-legal/lex-flow/commit/c9ac55e31c92a4a588d3f1822d995aa5a7f03205))

### Chores

- **deps**: Bump pypdf, rollup, and minimatch
  ([`c1e17f9`](https://github.com/inspira-legal/lex-flow/commit/c1e17f99446dc01d19d08462cb9cba72c2b9487a))

- **web**: Build frontend library [skip ci]
  ([`50557bf`](https://github.com/inspira-legal/lex-flow/commit/50557bf54aba6bdee8a4b0b0fa0aa07eb6e038a3))

- **web**: Release 1.14.0
  ([`f35af90`](https://github.com/inspira-legal/lex-flow/commit/f35af90952832b8c95a482fb9e99ae702d22e9b5))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`db3a2cc`](https://github.com/inspira-legal/lex-flow/commit/db3a2cc9266a6cb8a1bdd26bda3e859f45b93504))

### Features

- Add lex-flow-builder skill for workflow development
  ([#44](https://github.com/inspira-legal/lex-flow/pull/44),
  [`b381c23`](https://github.com/inspira-legal/lex-flow/commit/b381c23107f7b6a0d69116b994f9d11c6dc16ea8))

- **opcodes**: Add Apollo.io opcodes for lead generation
  ([#51](https://github.com/inspira-legal/lex-flow/pull/51),
  [`c9ac55e`](https://github.com/inspira-legal/lex-flow/commit/c9ac55e31c92a4a588d3f1822d995aa5a7f03205))

- **skill**: Add automated opcode synchronization system
  ([`005904a`](https://github.com/inspira-legal/lex-flow/commit/005904a71b144430aee129ea3c270383b2a5e5ca))


## v1.14.0 (2026-03-06)

### Bug Fixes

- **core**: Address code review findings for web search opcodes
  ([#45](https://github.com/inspira-legal/lex-flow/pull/45),
  [`0be3966`](https://github.com/inspira-legal/lex-flow/commit/0be3966fb7f666ca09f970cd9d1f385bc3b96ea7))

- **core**: Make client param optional for backward compatibility
  ([#45](https://github.com/inspira-legal/lex-flow/pull/45),
  [`0be3966`](https://github.com/inspira-legal/lex-flow/commit/0be3966fb7f666ca09f970cd9d1f385bc3b96ea7))

### Features

- **core**: Add api_key parameter to web search opcodes
  ([#45](https://github.com/inspira-legal/lex-flow/pull/45),
  [`0be3966`](https://github.com/inspira-legal/lex-flow/commit/0be3966fb7f666ca09f970cd9d1f385bc3b96ea7))

- **core**: Add client pattern to web search opcodes
  ([#45](https://github.com/inspira-legal/lex-flow/pull/45),
  [`0be3966`](https://github.com/inspira-legal/lex-flow/commit/0be3966fb7f666ca09f970cd9d1f385bc3b96ea7))


## v1.13.0 (2026-03-05)

### Features

- **core**: Add `all` optional dependency group
  ([`509de3b`](https://github.com/inspira-legal/lex-flow/commit/509de3b0cc8f475cf6916271f5a778376b0a2c12))


## v1.12.1 (2026-03-05)

### Bug Fixes

- **core**: Add guard for running engine without loaded program
  ([`418d7bc`](https://github.com/inspira-legal/lex-flow/commit/418d7bcec69b5995709ea02ae44f732d7c54bc23))

### Chores

- **cli**: Release 1.5.0
  ([`5366247`](https://github.com/inspira-legal/lex-flow/commit/5366247c7332b79c455b30299ab9415e7045c8d7))

- **web**: Release 1.13.0
  ([`0c3c965`](https://github.com/inspira-legal/lex-flow/commit/0c3c965bade6b8c3dc0468e13b140f41c12c8d74))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`8f3ee91`](https://github.com/inspira-legal/lex-flow/commit/8f3ee9131f3925088f31a279d20a6a9322a31f7a))


## v1.12.0 (2026-03-04)

### Bug Fixes

- **core**: Filter malformed results in hubspot_get_associations
  ([`d12bb44`](https://github.com/inspira-legal/lex-flow/commit/d12bb447d1f9ed51a02cac79465890e3d1e9c247))

### Chores

- **cli**: Release 1.4.0
  ([`acde866`](https://github.com/inspira-legal/lex-flow/commit/acde86605c9f6041d8abdcf3f640a5d4f3ca281e))

- **web**: Release 1.12.0
  ([`476d5ad`](https://github.com/inspira-legal/lex-flow/commit/476d5adec270a7f30566109d20cd2de2c366d9b1))

### Features

- **core**: Add hubspot_get_associations opcode
  ([`754ca42`](https://github.com/inspira-legal/lex-flow/commit/754ca42cddc9822fa48bad0dedc1e74aeee494fb))

### Testing

- **core**: Add tests for hubspot_get_associations opcode
  ([`9d68271`](https://github.com/inspira-legal/lex-flow/commit/9d68271f207014afd8648f96166eed5cf642384e))


## v1.11.0 (2026-03-02)

### Bug Fixes

- **ci**: Create GitHub releases during semantic-release version step
  ([#38](https://github.com/inspira-legal/lex-flow/pull/38),
  [`92d51f5`](https://github.com/inspira-legal/lex-flow/commit/92d51f52e3d2f504b6906c4733f6a6fbb820b6df))

- **ci**: Force semantic-release to push via SSH instead of HTTPS
  ([#41](https://github.com/inspira-legal/lex-flow/pull/41),
  [`3bb951b`](https://github.com/inspira-legal/lex-flow/commit/3bb951b7d4d7235a23902f475476d61f5a5782c2))

- **ci**: Use SSH remote for semantic-release push to bypass branch ruleset
  ([#39](https://github.com/inspira-legal/lex-flow/pull/39),
  [`77cce17`](https://github.com/inspira-legal/lex-flow/commit/77cce177bb3eba03a9642be26bfa0ba0a88c96a7))

- **ci**: Wire force_all input to release job conditions
  ([#40](https://github.com/inspira-legal/lex-flow/pull/40),
  [`fd88cb8`](https://github.com/inspira-legal/lex-flow/commit/fd88cb858ce7eab8145945a8b7e86c5adccaf5b8))

- **core**: Address code review findings for web search opcodes
  ([#24](https://github.com/inspira-legal/lex-flow/pull/24),
  [`59f9a3c`](https://github.com/inspira-legal/lex-flow/commit/59f9a3c9d2ba47193b7c7bba759025d578526bd0))

### Chores

- **web**: Build frontend library [skip ci]
  ([`ab71ccb`](https://github.com/inspira-legal/lex-flow/commit/ab71ccbe9cb7aec488462170a48853d6f5eb5fff))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`f1ce931`](https://github.com/inspira-legal/lex-flow/commit/f1ce9313e0ba87e4bfbdb8c82c34471f2bbfead2))

- Auto-update opcode reference and grammar [skip ci]
  ([`cb9b149`](https://github.com/inspira-legal/lex-flow/commit/cb9b14964ba8bc5115a14a6d57967eb6f4d0e536))

- Regenerate opcode reference after rebase with main
  ([#24](https://github.com/inspira-legal/lex-flow/pull/24),
  [`59f9a3c`](https://github.com/inspira-legal/lex-flow/commit/59f9a3c9d2ba47193b7c7bba759025d578526bd0))

### Features

- **core**: Add web search opcodes via Tavily API
  ([#24](https://github.com/inspira-legal/lex-flow/pull/24),
  [`59f9a3c`](https://github.com/inspira-legal/lex-flow/commit/59f9a3c9d2ba47193b7c7bba759025d578526bd0))

### Testing

- **core**: Add missing API key error tests for web search opcodes
  ([#24](https://github.com/inspira-legal/lex-flow/pull/24),
  [`59f9a3c`](https://github.com/inspira-legal/lex-flow/commit/59f9a3c9d2ba47193b7c7bba759025d578526bd0))


## v1.10.0 (2026-03-01)

### Bug Fixes

- **core**: Add slack-sdk to root pyproject.toml optional dependencies
  ([#21](https://github.com/inspira-legal/lex-flow/pull/21),
  [`8929cc3`](https://github.com/inspira-legal/lex-flow/commit/8929cc31b8c9557ca5a6c6312348b131a5fb9139))

### Chores

- **cli**: Release 1.3.0
  ([`8aed001`](https://github.com/inspira-legal/lex-flow/commit/8aed001b447d16265215685980087c077f7072f9))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`5191cf3`](https://github.com/inspira-legal/lex-flow/commit/5191cf3a1b9e9dc4f93bf83b54fadaddd9c2ede8))

- Create docs about slack opcodes connection
  ([#21](https://github.com/inspira-legal/lex-flow/pull/21),
  [`8929cc3`](https://github.com/inspira-legal/lex-flow/commit/8929cc31b8c9557ca5a6c6312348b131a5fb9139))

- Regenerate opcode reference with all dependencies installed
  ([#21](https://github.com/inspira-legal/lex-flow/pull/21),
  [`8929cc3`](https://github.com/inspira-legal/lex-flow/commit/8929cc31b8c9557ca5a6c6312348b131a5fb9139))

### Features

- **core**: Add Slack integration opcodes for messaging and workspace automation
  ([#21](https://github.com/inspira-legal/lex-flow/pull/21),
  [`8929cc3`](https://github.com/inspira-legal/lex-flow/commit/8929cc31b8c9557ca5a6c6312348b131a5fb9139))

### Testing

- **core**: Add comprehensive tests for Slack opcodes and fix docstring placeholder
  ([#21](https://github.com/inspira-legal/lex-flow/pull/21),
  [`8929cc3`](https://github.com/inspira-legal/lex-flow/commit/8929cc31b8c9557ca5a6c6312348b131a5fb9139))


## v1.9.1 (2026-02-24)

### Bug Fixes

- **core**: Address PR #25 review findings
  ([#25](https://github.com/inspira-legal/lex-flow/pull/25),
  [`6a1ccff`](https://github.com/inspira-legal/lex-flow/commit/6a1ccff35a856303d61d992d392ab5767b5407ea))

- **core**: Preserve generic type parameters in docs generation
  ([#25](https://github.com/inspira-legal/lex-flow/pull/25),
  [`6a1ccff`](https://github.com/inspira-legal/lex-flow/commit/6a1ccff35a856303d61d992d392ab5767b5407ea))

- **core**: Resolve race condition in release workflow
  ([#31](https://github.com/inspira-legal/lex-flow/pull/31),
  [`b1e58dc`](https://github.com/inspira-legal/lex-flow/commit/b1e58dcbf36851204639d57d557c78c80d9f87af))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`cf68617`](https://github.com/inspira-legal/lex-flow/commit/cf686173121691212b5683485afe7204482c6f47))


## v1.9.0 (2026-02-24)

### Bug Fixes

- Gemini suggestions security ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Add token redaction and graceful degradation test for HubSpot opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Address code review findings on HubSpot and AI opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Address PR review feedback on HubSpot opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Address PR review findings on HubSpot opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`69e0b3b`](https://github.com/inspira-legal/lex-flow/commit/69e0b3bd4983056872cfa1ec62847db9e1a9ecba))

- Regenerate opcode reference after rebase
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

### Features

- **core**: Add HubSpot CRM integration opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))


## v1.8.0 (2026-02-23)

### Bug Fixes

- **core**: Improve pgvector opcodes safety and test coverage
  ([#28](https://github.com/inspira-legal/lex-flow/pull/28),
  [`e26d6f9`](https://github.com/inspira-legal/lex-flow/commit/e26d6f9f69c3e81b1049bc0f73c97cec569711e9))

### Chores

- Add PR Multi Reviewers Claude Code skill
  ([#28](https://github.com/inspira-legal/lex-flow/pull/28),
  [`e26d6f9`](https://github.com/inspira-legal/lex-flow/commit/e26d6f9f69c3e81b1049bc0f73c97cec569711e9))

- Add PR Multi Reviewers Claude Code skill
  ([#29](https://github.com/inspira-legal/lex-flow/pull/29),
  [`cfd8d36`](https://github.com/inspira-legal/lex-flow/commit/cfd8d368afc69363443b95ed698546aa6376e4de))

- Add smart agent selection to PR review skill
  ([#28](https://github.com/inspira-legal/lex-flow/pull/28),
  [`e26d6f9`](https://github.com/inspira-legal/lex-flow/commit/e26d6f9f69c3e81b1049bc0f73c97cec569711e9))

- Add smart agent selection to PR review skill
  ([#29](https://github.com/inspira-legal/lex-flow/pull/29),
  [`cfd8d36`](https://github.com/inspira-legal/lex-flow/commit/cfd8d368afc69363443b95ed698546aa6376e4de))

- **web**: Build frontend library [skip ci]
  ([`357050e`](https://github.com/inspira-legal/lex-flow/commit/357050e0de72e609b26a60ad49699ca2eacbade1))

- **web**: Release 1.11.0
  ([`6075580`](https://github.com/inspira-legal/lex-flow/commit/6075580cd8d7973d8ba3863c2df2e249cba9243f))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`f172262`](https://github.com/inspira-legal/lex-flow/commit/f1722629ef05deeca1b24177cb9d6dd9ff6c237a))

### Features

- **opcodes**: Creates pgvector opcodes ([#28](https://github.com/inspira-legal/lex-flow/pull/28),
  [`e26d6f9`](https://github.com/inspira-legal/lex-flow/commit/e26d6f9f69c3e81b1049bc0f73c97cec569711e9))


## v1.7.0 (2026-02-23)

### Bug Fixes

- **sheets**: Address PR review feedback for async and parameter naming
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **sheets**: Address PR review — sheet name quoting, path validation, and lock file
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **sheets**: Query full sheet range in sheets_get_last_row
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **sheets**: Strengthen path traversal protection in sheets_create_client
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

### Chores

- Add CODEOWNERS file ([#19](https://github.com/inspira-legal/lex-flow/pull/19),
  [`815c882`](https://github.com/inspira-legal/lex-flow/commit/815c8828759365eca4fb5da1fe18f9d2aca4e2fe))

- **deps**: Bump cryptography from 46.0.4 to 46.0.5
  ([#19](https://github.com/inspira-legal/lex-flow/pull/19),
  [`815c882`](https://github.com/inspira-legal/lex-flow/commit/815c8828759365eca4fb5da1fe18f9d2aca4e2fe))

- **deps**: Bump cryptography from 46.0.4 to 46.0.5 in /lexflow-core
  ([#20](https://github.com/inspira-legal/lex-flow/pull/20),
  [`c670e49`](https://github.com/inspira-legal/lex-flow/commit/c670e49d77918cf17581943b2587e682fbf1c832))

- **deps**: Bump pydantic-ai-slim from 1.0.1 to 1.56.0
  ([#17](https://github.com/inspira-legal/lex-flow/pull/17),
  [`7de030f`](https://github.com/inspira-legal/lex-flow/commit/7de030f124f2cd5e8797dd46d4f4d0c234fbf45f))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`e47d536`](https://github.com/inspira-legal/lex-flow/commit/e47d536f7413c72ce2f7705a96abe33325eaa4a9))

### Features

- **pr-template**: Add pull request template for consistent PR submissions
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **sheets**: Add examples for appending and reading data from Google Sheets
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **sheets**: Add Google Sheets integration with opcodes and examples
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **sheets**: Add Google Sheets operations and update dependencies
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **sheets**: Add unit tests, fix optional dependency pattern, and add integration test workflow
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))


## v1.6.0 (2026-02-18)

### Bug Fixes

- **ai**: Address code review findings — imports, types, tests, style
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **ai**: Address PR #8 review — remove ContextVar, fix private attrs, add tests
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **docs**: Add hardcoded secrets warning to security section in code review guide
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- **docs**: Correct exception type and private attribute in code review guide examples
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- **docs**: Fix inconsistent abbreviation, fictional exception, and inaccurate pattern ref in code
  review guide ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- **docs**: Fix link text, commit types, and hardcoded line ref in code review guide
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- **docs**: Remove fictional references and soften overstated rules in code review guide
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- **docs**: Resolve undefined rule ID prefixes in code review guide
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- **examples**: Fix typo and add debug prints to workflow_as_tools
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

### Chores

- **web**: Build frontend library [skip ci]
  ([`c765070`](https://github.com/inspira-legal/lex-flow/commit/c7650708687c5322e88c6bc2f8fbd44f8bfaf4c0))

- **web**: Release 1.10.0
  ([`833b8b7`](https://github.com/inspira-legal/lex-flow/commit/833b8b7529d2dd5a8ff026f59580215ad23f3545))

### Documentation

- Add code review guide and Gemini styleguide for automated PR reviews
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- Add code review guide and styleguide for automated PR reviews
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- Auto-update opcode reference and grammar [skip ci]
  ([`b4c9b1d`](https://github.com/inspira-legal/lex-flow/commit/b4c9b1d840beab82d96e0030fb4e33cb8e6f6e9b))

### Features

- **ai**: Add ai_agent_with_tools opcode for agentic workflows
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **ai**: Allow workflows as tools in ai_agent_with_tools
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **core**: Add privileged opcode injection system
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))


## v1.5.0 (2026-02-07)

### Bug Fixes

- **ci**: Use SSH deploy key for semantic-release push instead of GITHUB_TOKEN
  ([`d5491b9`](https://github.com/inspira-legal/lex-flow/commit/d5491b92b2f2c7333efa8a908be63387511ab1dd))

- **rag**: Fix RAG pipeline workflows and add BM25 reranking
  ([`4ae28fa`](https://github.com/inspira-legal/lex-flow/commit/4ae28fa73fb14457b9c1d12847287ba26c5e02f4))

- **web**: Add --no-vcs-release to version step, let publish create GitHub release
  ([`6f0581e`](https://github.com/inspira-legal/lex-flow/commit/6f0581ed3e0f1756101aae596bfc04e8093b308a))

- **web**: Add missing gcs category to grammar and node palette
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **web**: Strip pubsub_ and async_ prefixes in node palette display names
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

### Chores

- **web**: Build frontend library [skip ci]
  ([`35a1ad9`](https://github.com/inspira-legal/lex-flow/commit/35a1ad9f35fbe960317ea0e7632b1bdc0a12b2b1))

- **web**: Release 1.8.0
  ([`9533fb9`](https://github.com/inspira-legal/lex-flow/commit/9533fb97e50d1e0828217d5792f0272c8b1bec05))

- **web**: Release 1.9.0
  ([`815f888`](https://github.com/inspira-legal/lex-flow/commit/815f888a841d89e454dfd8f57bc74a661faf4ff3))

- **web**: Release 1.9.1
  ([`7086800`](https://github.com/inspira-legal/lex-flow/commit/70868009964ba347b672af850fa1e3f8d14f56ec))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`10d8af6`](https://github.com/inspira-legal/lex-flow/commit/10d8af6b3efd864db1df403ab5a9547b99f16798))

### Features

- **core**: Add Google Cloud Pub/Sub opcodes
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **core**: Add long-running deployment docs to agent instructions
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **core**: PubSub Opcodes(#12)
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **web**: Add detailed interface inputs support (name, type, required)
  ([`d360a6e`](https://github.com/inspira-legal/lex-flow/commit/d360a6e80085a44fa16e8a987bf504b9f354d651))

- **web**: Trigerring new release updated editor
  ([`72152b8`](https://github.com/inspira-legal/lex-flow/commit/72152b875b6109f549c5da7b84361b29302fb118))


## v1.4.0 (2026-02-05)

### Bug Fixes

- **gcs**: Use asyncio.to_thread for non-blocking I/O operations
  ([`60c040f`](https://github.com/inspira-legal/lex-flow/commit/60c040f2dcd53cc74c99d77b517b45def5ac3528))

### Chores

- **cli**: Release 1.2.0
  ([`6e5c163`](https://github.com/inspira-legal/lex-flow/commit/6e5c1630da77dacd6c1b08006d1862118dd4d4ee))

- **web**: Build frontend library [skip ci]
  ([`a559d9a`](https://github.com/inspira-legal/lex-flow/commit/a559d9ae8ad81fefc301d16df8dcca23b0bc7afa))

- **web**: Release 1.7.0
  ([`e48215a`](https://github.com/inspira-legal/lex-flow/commit/e48215a01541a4020538eba74a264d2f314d5c34))

- **web**: Remove grammar.json from tracking, copy from core at build time
  ([`0014e93`](https://github.com/inspira-legal/lex-flow/commit/0014e937a2fff95d71a5912fb7d98b51f2d8978c))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`2f5dd59`](https://github.com/inspira-legal/lex-flow/commit/2f5dd5937e5ecec7edd3ab20912bd8b2deb1e83f))

### Features

- **core**: Add Google Cloud Storage integration
  ([`f3253da`](https://github.com/inspira-legal/lex-flow/commit/f3253da57f396bfd22c75b4016049aad36ac833d))

- **rag**: Add GCS ingestion workflow and RAG improvements
  ([`a1428a0`](https://github.com/inspira-legal/lex-flow/commit/a1428a09e48779d07ad86a6d466bc46184ddc0b1))

### Refactoring

- **gcs**: Address PR review comments
  ([`a0e3cca`](https://github.com/inspira-legal/lex-flow/commit/a0e3ccac78edd17f14b0ee5b09e480d27438ead8))


## v1.3.0 (2026-02-04)

### Chores

- Add CI auto-docs generation and gitignore frontend grammar
  ([`498f32f`](https://github.com/inspira-legal/lex-flow/commit/498f32fc02de4a442b751a4d46f84886cb68f540))

### Features

- **cli**: Add grammar sync command
  ([`3e61814`](https://github.com/inspira-legal/lex-flow/commit/3e61814015699476aaac63ad5325c022fcfd8cac))

- **core**: Add self-describing opcode category system
  ([`11f15bc`](https://github.com/inspira-legal/lex-flow/commit/11f15bc0723ec8bad019ea70d703e164a6c5b3b1))

- **web**: Use explicit category from API for opcode grouping
  ([`51d6314`](https://github.com/inspira-legal/lex-flow/commit/51d63149e9bf4373603badcb2afb3167420b3f8b))


## v1.2.0 (2026-02-03)

### Bug Fixes

- **web**: Expand entire reporter chain and fix bounding box calculation
  ([`833b001`](https://github.com/inspira-legal/lex-flow/commit/833b0015cbadc9b8f83b7756cd18afec02b71e7d))

- **web**: Properly cleanup WebSocket tasks on disconnect
  ([`fa5e341`](https://github.com/inspira-legal/lex-flow/commit/fa5e3411742154b4c1260ff6239f4db14389c2ed))

- **web**: Use composite IDs for node namespacing in visual editor
  ([`fead6b7`](https://github.com/inspira-legal/lex-flow/commit/fead6b790ffc7383eeb799efc17cd90795ad6340))

- **web**: Use jsDelivr CDN instead of GitHub release assets
  ([`d4521fa`](https://github.com/inspira-legal/lex-flow/commit/d4521facbaa45e5976d1f5a3c76db166a4918005))

- **web**: Wire execution override into WebSocket hook
  ([`82633ea`](https://github.com/inspira-legal/lex-flow/commit/82633ea22b3e30563b096acb9dee0eb912f24d6d))

### Chores

- Pin python version to 3.13
  ([`1135ee6`](https://github.com/inspira-legal/lex-flow/commit/1135ee69e29a4f3547c3df021b4be91ea914a335))

- **cli**: Release 1.1.0
  ([`55afa40`](https://github.com/inspira-legal/lex-flow/commit/55afa40d74f37f517f801ff6ceb78558480ee50f))

- **web**: Build frontend library [skip ci]
  ([`e2c05b4`](https://github.com/inspira-legal/lex-flow/commit/e2c05b4b277ba7954df7ca9771b8a34c7316d45f))

- **web**: Build frontend library [skip ci]
  ([`113565e`](https://github.com/inspira-legal/lex-flow/commit/113565ec0fb59b6e3f0b79b43a69898757b424ed))

- **web**: Build frontend library [skip ci]
  ([`420135a`](https://github.com/inspira-legal/lex-flow/commit/420135a80f1d6f3ce770b3c204426b0dbddd6398))

- **web**: Build frontend library [skip ci]
  ([`43ac2c1`](https://github.com/inspira-legal/lex-flow/commit/43ac2c15044fedd5064a5321f1f1d95332796532))

- **web**: Build frontend library [skip ci]
  ([`0096067`](https://github.com/inspira-legal/lex-flow/commit/0096067f1cce018081d9b29999fd9f8bfb9240ab))

- **web**: Build frontend library [skip ci]
  ([`4054ad8`](https://github.com/inspira-legal/lex-flow/commit/4054ad8fc06be0c850feefbbf51fbae73b7fbf67))

- **web**: Release 1.3.0
  ([`d856a46`](https://github.com/inspira-legal/lex-flow/commit/d856a4699cf219478240a12eaa0a23e85876e631))

- **web**: Release 1.3.1
  ([`8630135`](https://github.com/inspira-legal/lex-flow/commit/8630135d9f81467c4eae3764d952e40e4e1eb3b2))

- **web**: Release 1.4.0
  ([`b2c90ec`](https://github.com/inspira-legal/lex-flow/commit/b2c90ec64b5c3a341af351758dc6f53654353698))

- **web**: Release 1.5.0
  ([`390c647`](https://github.com/inspira-legal/lex-flow/commit/390c647b50483e42151055e45f707d7259ff2fbb))

- **web**: Release 1.5.1
  ([`70aa1e4`](https://github.com/inspira-legal/lex-flow/commit/70aa1e447dfaf2110ea6f05364d53d32427408d1))

- **web**: Release 1.6.0
  ([`905a1de`](https://github.com/inspira-legal/lex-flow/commit/905a1de40f7a85bdfb1f0d2415c8696997ea94d9))

- **web**: Release 1.6.1
  ([`7dac326`](https://github.com/inspira-legal/lex-flow/commit/7dac326166152c3d7e891e861080cd9c820ebfcd))

- **web**: Release 1.6.2
  ([`7c2165e`](https://github.com/inspira-legal/lex-flow/commit/7c2165e472262d9c369e168382bc65b156247f04))

### Documentation

- Add claude.md file to repo
  ([`9adc6cc`](https://github.com/inspira-legal/lex-flow/commit/9adc6ccb97ee9556d3f3dac176696c8ddac099bd))

- Add README for monorepo and lexflow-web
  ([`a8a5e79`](https://github.com/inspira-legal/lex-flow/commit/a8a5e793dad6ee73f712f49743338af51eaffe32))

- Updating claude.md
  ([`9f75f98`](https://github.com/inspira-legal/lex-flow/commit/9f75f9848b68b21ad9f3725a72f52781ab6774e2))

- Use uv instead of pip in README examples
  ([`488a5d6`](https://github.com/inspira-legal/lex-flow/commit/488a5d65dd735d411292da1b03a03b78fa3b734d))

### Features

- **web**: Add embeddable editor library
  ([`9a09f05`](https://github.com/inspira-legal/lex-flow/commit/9a09f054ada301e3527d09a77097de7a5b8ce41d))

- **web**: Add extract to workflow feature
  ([`cfa5ee6`](https://github.com/inspira-legal/lex-flow/commit/cfa5ee61c6d60c52fcc07f345fdc25b7842729a7))

- **web**: Add save button, execution override, and custom opcode URL support
  ([`de6b01a`](https://github.com/inspira-legal/lex-flow/commit/de6b01ae3777dbfe7cc012901531f265dc678c67))

- **web**: Add workflow create/delete and fix start node wiring
  ([`521aec5`](https://github.com/inspira-legal/lex-flow/commit/521aec53feb0740f30b8a268459bd4fccd6439d8))

### Refactoring

- **web**: Replace context vars with channels for web opcodes
  ([`0ef42d6`](https://github.com/inspira-legal/lex-flow/commit/0ef42d67fec29ed9bdf50cf906da1b9a9eb77426))


## v1.1.0 (2026-01-30)

### Bug Fixes

- Add git pull to release workflow to handle sequential releases
  ([`96fafad`](https://github.com/inspira-legal/lex-flow/commit/96fafad48c8d1f5c984c167709b5fd9d69e1cbde))

- **web**: Improve workflow drop target detection
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

### Chores

- Add pre-commit hooks for code quality and docs generation
  ([`3d981d4`](https://github.com/inspira-legal/lex-flow/commit/3d981d41ce2b4b214c7d2126ac1889f38ecb1bb0))

- Add workflow_dispatch trigger and update package docstrings
  ([`7531437`](https://github.com/inspira-legal/lex-flow/commit/7531437793d1e0bd4d0afaa402b7923bfb36e9c7))

- Update lock file ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **cli**: Release 1.0.0
  ([`c606f98`](https://github.com/inspira-legal/lex-flow/commit/c606f984ca54e0f0ad46ecba5dcc9a9334d9b771))

- **docs**: Removing unused documentation. ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Release 1.0.0
  ([`e7b3df6`](https://github.com/inspira-legal/lex-flow/commit/e7b3df6aba948578cca6a750724baf2412f3d647))

- **web**: Release 1.1.0
  ([`6e5eb68`](https://github.com/inspira-legal/lex-flow/commit/6e5eb68cc4e13ca43edc325d718d9d18de3f6100))

- **web**: Release 1.2.0
  ([`997421f`](https://github.com/inspira-legal/lex-flow/commit/997421fd99386ee638ff6d8c452121e67b7a532a))

- **web**: Remove deprecated CSS module components
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Remove example pngs
  ([`57f049b`](https://github.com/inspira-legal/lex-flow/commit/57f049b516d5a4db7cf02e342237683b36ca78db))

- **web**: Update build artifacts ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Update build configuration and dependencies
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

### Documentation

- Regenerate opcode reference
  ([`f163fea`](https://github.com/inspira-legal/lex-flow/commit/f163feac9a34f84d9853933c9506053320924500))

- Simplify docs README
  ([`2ae0249`](https://github.com/inspira-legal/lex-flow/commit/2ae0249a1eca8fe1bcd1adbd4fbd0c9128f785f8))

- Update agents to reference auto-generated docs
  ([`26a1fd7`](https://github.com/inspira-legal/lex-flow/commit/26a1fd78ee1efef63ce6b12f653c9e7435a3af1f))

- Update getting started and fix examples README links
  ([`d7cd50f`](https://github.com/inspira-legal/lex-flow/commit/d7cd50fa908add4cf07cc105470e4500d5c282bf))

- Updating docs
  ([`fa50c84`](https://github.com/inspira-legal/lex-flow/commit/fa50c84568ca452884302d2b055f09fb849102dd))

- **web**: Add redesign documentation ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

### Features

- **web**: Add confirm dialog state management
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Add design system foundation ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Add grammar-driven dynamic node rendering
  ([`37621db`](https://github.com/inspira-legal/lex-flow/commit/37621db67e63cc1b48c4f9fc1ddac62d5575d8f1))

- **web**: Add UI component library ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Major frontend re-design and documentation cleanup
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Redesign and unify node editor components
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Redesign canvas and visualization components
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Redesign code editor component ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Redesign execution panel components
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Redesign layout components ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Redesign node palette components ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Update application to use redesigned components
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

### Refactoring

- **web**: Separate editing logic from rendering
  ([`03083f6`](https://github.com/inspira-legal/lex-flow/commit/03083f614ff64ab3760d1e9283d8619dcd400a77))


## v1.0.0 (2026-01-29)

- Initial Release
