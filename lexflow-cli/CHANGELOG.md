# CHANGELOG

<!-- version list -->

## v1.3.0 (2026-02-24)

### Bug Fixes

- Gemini suggestions security ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **ai**: Address code review findings — imports, types, tests, style
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **ai**: Address PR #8 review — remove ContextVar, fix private attrs, add tests
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **ci**: Use SSH deploy key for semantic-release push instead of GITHUB_TOKEN
  ([`d5491b9`](https://github.com/inspira-legal/lex-flow/commit/d5491b92b2f2c7333efa8a908be63387511ab1dd))

- **core**: Add token redaction and graceful degradation test for HubSpot opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Address code review findings on HubSpot and AI opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Address PR #25 review findings
  ([#25](https://github.com/inspira-legal/lex-flow/pull/25),
  [`6a1ccff`](https://github.com/inspira-legal/lex-flow/commit/6a1ccff35a856303d61d992d392ab5767b5407ea))

- **core**: Address PR review feedback on HubSpot opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Address PR review findings on HubSpot opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Improve pgvector opcodes safety and test coverage
  ([#28](https://github.com/inspira-legal/lex-flow/pull/28),
  [`e26d6f9`](https://github.com/inspira-legal/lex-flow/commit/e26d6f9f69c3e81b1049bc0f73c97cec569711e9))

- **core**: Preserve generic type parameters in docs generation
  ([#25](https://github.com/inspira-legal/lex-flow/pull/25),
  [`6a1ccff`](https://github.com/inspira-legal/lex-flow/commit/6a1ccff35a856303d61d992d392ab5767b5407ea))

- **core**: Resolve race condition in release workflow
  ([#31](https://github.com/inspira-legal/lex-flow/pull/31),
  [`b1e58dc`](https://github.com/inspira-legal/lex-flow/commit/b1e58dcbf36851204639d57d557c78c80d9f87af))

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

- **gcs**: Use asyncio.to_thread for non-blocking I/O operations
  ([`60c040f`](https://github.com/inspira-legal/lex-flow/commit/60c040f2dcd53cc74c99d77b517b45def5ac3528))

- **rag**: Fix RAG pipeline workflows and add BM25 reranking
  ([`4ae28fa`](https://github.com/inspira-legal/lex-flow/commit/4ae28fa73fb14457b9c1d12847287ba26c5e02f4))

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

- **web**: Add --no-vcs-release to version step, let publish create GitHub release
  ([`6f0581e`](https://github.com/inspira-legal/lex-flow/commit/6f0581ed3e0f1756101aae596bfc04e8093b308a))

- **web**: Add missing gcs category to grammar and node palette
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **web**: Strip pubsub_ and async_ prefixes in node palette display names
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

### Chores

- Add CODEOWNERS file ([#19](https://github.com/inspira-legal/lex-flow/pull/19),
  [`815c882`](https://github.com/inspira-legal/lex-flow/commit/815c8828759365eca4fb5da1fe18f9d2aca4e2fe))

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

- **core**: Release 1.4.0
  ([`a386b8a`](https://github.com/inspira-legal/lex-flow/commit/a386b8a9efc132247e8cfb81b7809ea6e364508f))

- **core**: Release 1.5.0
  ([`0ced13d`](https://github.com/inspira-legal/lex-flow/commit/0ced13df9391ba444b53a54594c6c4f4a47bbddb))

- **core**: Release 1.6.0
  ([`84b88f9`](https://github.com/inspira-legal/lex-flow/commit/84b88f9d3f0c6f76dd457eb5b1b9c686d6729b7b))

- **core**: Release 1.7.0
  ([`40da529`](https://github.com/inspira-legal/lex-flow/commit/40da529126adc67196c0db8a38ccb1a0816aa403))

- **core**: Release 1.8.0
  ([`15dfd03`](https://github.com/inspira-legal/lex-flow/commit/15dfd039bca52efcbfdcd8689d7335f100933372))

- **core**: Release 1.9.0
  ([`5165740`](https://github.com/inspira-legal/lex-flow/commit/51657409510b55f6947ad3c17c9ec7fbfce655f7))

- **core**: Release 1.9.1
  ([`8953d4f`](https://github.com/inspira-legal/lex-flow/commit/8953d4fccf29d517aad6433397f6a3ebe6094146))

- **deps**: Bump cryptography from 46.0.4 to 46.0.5
  ([#19](https://github.com/inspira-legal/lex-flow/pull/19),
  [`815c882`](https://github.com/inspira-legal/lex-flow/commit/815c8828759365eca4fb5da1fe18f9d2aca4e2fe))

- **deps**: Bump cryptography from 46.0.4 to 46.0.5 in /lexflow-core
  ([#20](https://github.com/inspira-legal/lex-flow/pull/20),
  [`c670e49`](https://github.com/inspira-legal/lex-flow/commit/c670e49d77918cf17581943b2587e682fbf1c832))

- **deps**: Bump pydantic-ai-slim from 1.0.1 to 1.56.0
  ([#17](https://github.com/inspira-legal/lex-flow/pull/17),
  [`7de030f`](https://github.com/inspira-legal/lex-flow/commit/7de030f124f2cd5e8797dd46d4f4d0c234fbf45f))

- **web**: Build frontend library [skip ci]
  ([`357050e`](https://github.com/inspira-legal/lex-flow/commit/357050e0de72e609b26a60ad49699ca2eacbade1))

- **web**: Build frontend library [skip ci]
  ([`c765070`](https://github.com/inspira-legal/lex-flow/commit/c7650708687c5322e88c6bc2f8fbd44f8bfaf4c0))

- **web**: Build frontend library [skip ci]
  ([`35a1ad9`](https://github.com/inspira-legal/lex-flow/commit/35a1ad9f35fbe960317ea0e7632b1bdc0a12b2b1))

- **web**: Build frontend library [skip ci]
  ([`a559d9a`](https://github.com/inspira-legal/lex-flow/commit/a559d9ae8ad81fefc301d16df8dcca23b0bc7afa))

- **web**: Release 1.10.0
  ([`833b8b7`](https://github.com/inspira-legal/lex-flow/commit/833b8b7529d2dd5a8ff026f59580215ad23f3545))

- **web**: Release 1.11.0
  ([`6075580`](https://github.com/inspira-legal/lex-flow/commit/6075580cd8d7973d8ba3863c2df2e249cba9243f))

- **web**: Release 1.7.0
  ([`e48215a`](https://github.com/inspira-legal/lex-flow/commit/e48215a01541a4020538eba74a264d2f314d5c34))

- **web**: Release 1.8.0
  ([`9533fb9`](https://github.com/inspira-legal/lex-flow/commit/9533fb97e50d1e0828217d5792f0272c8b1bec05))

- **web**: Release 1.9.0
  ([`815f888`](https://github.com/inspira-legal/lex-flow/commit/815f888a841d89e454dfd8f57bc74a661faf4ff3))

- **web**: Release 1.9.1
  ([`7086800`](https://github.com/inspira-legal/lex-flow/commit/70868009964ba347b672af850fa1e3f8d14f56ec))

- **web**: Remove grammar.json from tracking, copy from core at build time
  ([`0014e93`](https://github.com/inspira-legal/lex-flow/commit/0014e937a2fff95d71a5912fb7d98b51f2d8978c))

### Documentation

- Add code review guide and Gemini styleguide for automated PR reviews
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- Add code review guide and styleguide for automated PR reviews
  ([#23](https://github.com/inspira-legal/lex-flow/pull/23),
  [`d1e0f5b`](https://github.com/inspira-legal/lex-flow/commit/d1e0f5b958998c98017c93472b91d383dd5e4751))

- Auto-update opcode reference and grammar [skip ci]
  ([`5191cf3`](https://github.com/inspira-legal/lex-flow/commit/5191cf3a1b9e9dc4f93bf83b54fadaddd9c2ede8))

- Auto-update opcode reference and grammar [skip ci]
  ([`cf68617`](https://github.com/inspira-legal/lex-flow/commit/cf686173121691212b5683485afe7204482c6f47))

- Auto-update opcode reference and grammar [skip ci]
  ([`69e0b3b`](https://github.com/inspira-legal/lex-flow/commit/69e0b3bd4983056872cfa1ec62847db9e1a9ecba))

- Auto-update opcode reference and grammar [skip ci]
  ([`f172262`](https://github.com/inspira-legal/lex-flow/commit/f1722629ef05deeca1b24177cb9d6dd9ff6c237a))

- Auto-update opcode reference and grammar [skip ci]
  ([`e47d536`](https://github.com/inspira-legal/lex-flow/commit/e47d536f7413c72ce2f7705a96abe33325eaa4a9))

- Auto-update opcode reference and grammar [skip ci]
  ([`b4c9b1d`](https://github.com/inspira-legal/lex-flow/commit/b4c9b1d840beab82d96e0030fb4e33cb8e6f6e9b))

- Auto-update opcode reference and grammar [skip ci]
  ([`10d8af6`](https://github.com/inspira-legal/lex-flow/commit/10d8af6b3efd864db1df403ab5a9547b99f16798))

- Regenerate opcode reference after rebase
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

### Features

- **ai**: Add ai_agent_with_tools opcode for agentic workflows
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **ai**: Allow workflows as tools in ai_agent_with_tools
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **core**: Add Google Cloud Pub/Sub opcodes
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **core**: Add Google Cloud Storage integration
  ([`f3253da`](https://github.com/inspira-legal/lex-flow/commit/f3253da57f396bfd22c75b4016049aad36ac833d))

- **core**: Add HubSpot CRM integration opcodes
  ([#18](https://github.com/inspira-legal/lex-flow/pull/18),
  [`edca1fa`](https://github.com/inspira-legal/lex-flow/commit/edca1fa8f130cc5294097cf11ea4b528216bce1e))

- **core**: Add long-running deployment docs to agent instructions
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **core**: Add privileged opcode injection system
  ([#8](https://github.com/inspira-legal/lex-flow/pull/8),
  [`b43b38b`](https://github.com/inspira-legal/lex-flow/commit/b43b38b53739d04e89560ff1dca4b942d77da776))

- **core**: PubSub Opcodes(#12)
  ([`4dc265b`](https://github.com/inspira-legal/lex-flow/commit/4dc265bd3fcfd750dcc1292a61c81ce7492e536c))

- **opcodes**: Creates pgvector opcodes ([#28](https://github.com/inspira-legal/lex-flow/pull/28),
  [`e26d6f9`](https://github.com/inspira-legal/lex-flow/commit/e26d6f9f69c3e81b1049bc0f73c97cec569711e9))

- **pr-template**: Add pull request template for consistent PR submissions
  ([#14](https://github.com/inspira-legal/lex-flow/pull/14),
  [`e8a77b5`](https://github.com/inspira-legal/lex-flow/commit/e8a77b5ae7d46e430f761e8a9f00ee1caf0b412a))

- **rag**: Add GCS ingestion workflow and RAG improvements
  ([`a1428a0`](https://github.com/inspira-legal/lex-flow/commit/a1428a09e48779d07ad86a6d466bc46184ddc0b1))

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

- **web**: Add detailed interface inputs support (name, type, required)
  ([`d360a6e`](https://github.com/inspira-legal/lex-flow/commit/d360a6e80085a44fa16e8a987bf504b9f354d651))

- **web**: Trigerring new release updated editor
  ([`72152b8`](https://github.com/inspira-legal/lex-flow/commit/72152b875b6109f549c5da7b84361b29302fb118))

### Refactoring

- **gcs**: Address PR review comments
  ([`a0e3cca`](https://github.com/inspira-legal/lex-flow/commit/a0e3ccac78edd17f14b0ee5b09e480d27438ead8))


## v1.2.0 (2026-02-04)

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

- Add CI auto-docs generation and gitignore frontend grammar
  ([`498f32f`](https://github.com/inspira-legal/lex-flow/commit/498f32fc02de4a442b751a4d46f84886cb68f540))

- Pin python version to 3.13
  ([`1135ee6`](https://github.com/inspira-legal/lex-flow/commit/1135ee69e29a4f3547c3df021b4be91ea914a335))

- **core**: Release 1.2.0
  ([`bef3589`](https://github.com/inspira-legal/lex-flow/commit/bef3589c81eddc5d4c2b27abe524afa489b902b0))

- **core**: Release 1.3.0
  ([`cc0e7f9`](https://github.com/inspira-legal/lex-flow/commit/cc0e7f954d94f3ac34c897c2f24dfd8f67e2416f))

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

- Auto-update opcode reference and grammar [skip ci]
  ([`2f5dd59`](https://github.com/inspira-legal/lex-flow/commit/2f5dd5937e5ecec7edd3ab20912bd8b2deb1e83f))

- Updating claude.md
  ([`9f75f98`](https://github.com/inspira-legal/lex-flow/commit/9f75f9848b68b21ad9f3725a72f52781ab6774e2))

- Use uv instead of pip in README examples
  ([`488a5d6`](https://github.com/inspira-legal/lex-flow/commit/488a5d65dd735d411292da1b03a03b78fa3b734d))

### Features

- **cli**: Add grammar sync command
  ([`3e61814`](https://github.com/inspira-legal/lex-flow/commit/3e61814015699476aaac63ad5325c022fcfd8cac))

- **core**: Add self-describing opcode category system
  ([`11f15bc`](https://github.com/inspira-legal/lex-flow/commit/11f15bc0723ec8bad019ea70d703e164a6c5b3b1))

- **web**: Add embeddable editor library
  ([`9a09f05`](https://github.com/inspira-legal/lex-flow/commit/9a09f054ada301e3527d09a77097de7a5b8ce41d))

- **web**: Add extract to workflow feature
  ([`cfa5ee6`](https://github.com/inspira-legal/lex-flow/commit/cfa5ee61c6d60c52fcc07f345fdc25b7842729a7))

- **web**: Add save button, execution override, and custom opcode URL support
  ([`de6b01a`](https://github.com/inspira-legal/lex-flow/commit/de6b01ae3777dbfe7cc012901531f265dc678c67))

- **web**: Add workflow create/delete and fix start node wiring
  ([`521aec5`](https://github.com/inspira-legal/lex-flow/commit/521aec53feb0740f30b8a268459bd4fccd6439d8))

- **web**: Use explicit category from API for opcode grouping
  ([`51d6314`](https://github.com/inspira-legal/lex-flow/commit/51d63149e9bf4373603badcb2afb3167420b3f8b))

### Refactoring

- **web**: Replace context vars with channels for web opcodes
  ([`0ef42d6`](https://github.com/inspira-legal/lex-flow/commit/0ef42d67fec29ed9bdf50cf906da1b9a9eb77426))


## v1.1.0 (2026-01-30)

### Bug Fixes

- **web**: Improve workflow drop target detection
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

### Chores

- Add pre-commit hooks for code quality and docs generation
  ([`3d981d4`](https://github.com/inspira-legal/lex-flow/commit/3d981d41ce2b4b214c7d2126ac1889f38ecb1bb0))

- Update lock file ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **core**: Release 1.1.0
  ([`e91b3dc`](https://github.com/inspira-legal/lex-flow/commit/e91b3dcc6f62de5a3fd0c74947fa4b10dfd6f904))

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
