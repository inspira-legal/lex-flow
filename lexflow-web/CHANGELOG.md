# CHANGELOG

<!-- version list -->

## v1.7.0 (2026-02-04)

### Chores

- Add CI auto-docs generation and gitignore frontend grammar
  ([`498f32f`](https://github.com/inspira-legal/lex-flow/commit/498f32fc02de4a442b751a4d46f84886cb68f540))

- **cli**: Release 1.2.0
  ([`6e5c163`](https://github.com/inspira-legal/lex-flow/commit/6e5c1630da77dacd6c1b08006d1862118dd4d4ee))

- **core**: Release 1.2.0
  ([`bef3589`](https://github.com/inspira-legal/lex-flow/commit/bef3589c81eddc5d4c2b27abe524afa489b902b0))

- **core**: Release 1.3.0
  ([`cc0e7f9`](https://github.com/inspira-legal/lex-flow/commit/cc0e7f954d94f3ac34c897c2f24dfd8f67e2416f))

- **web**: Build frontend library [skip ci]
  ([`a559d9a`](https://github.com/inspira-legal/lex-flow/commit/a559d9ae8ad81fefc301d16df8dcca23b0bc7afa))

### Documentation

- Auto-update opcode reference and grammar [skip ci]
  ([`2f5dd59`](https://github.com/inspira-legal/lex-flow/commit/2f5dd5937e5ecec7edd3ab20912bd8b2deb1e83f))

- Updating claude.md
  ([`9f75f98`](https://github.com/inspira-legal/lex-flow/commit/9f75f9848b68b21ad9f3725a72f52781ab6774e2))

### Features

- **cli**: Add grammar sync command
  ([`3e61814`](https://github.com/inspira-legal/lex-flow/commit/3e61814015699476aaac63ad5325c022fcfd8cac))

- **core**: Add self-describing opcode category system
  ([`11f15bc`](https://github.com/inspira-legal/lex-flow/commit/11f15bc0723ec8bad019ea70d703e164a6c5b3b1))

- **web**: Use explicit category from API for opcode grouping
  ([`51d6314`](https://github.com/inspira-legal/lex-flow/commit/51d63149e9bf4373603badcb2afb3167420b3f8b))


## v1.6.2 (2026-02-03)

### Bug Fixes

- **web**: Expand entire reporter chain and fix bounding box calculation
  ([`833b001`](https://github.com/inspira-legal/lex-flow/commit/833b0015cbadc9b8f83b7756cd18afec02b71e7d))

### Chores

- Pin python version to 3.13
  ([`1135ee6`](https://github.com/inspira-legal/lex-flow/commit/1135ee69e29a4f3547c3df021b4be91ea914a335))

- **web**: Build frontend library [skip ci]
  ([`e2c05b4`](https://github.com/inspira-legal/lex-flow/commit/e2c05b4b277ba7954df7ca9771b8a34c7316d45f))

### Documentation

- Add claude.md file to repo
  ([`9adc6cc`](https://github.com/inspira-legal/lex-flow/commit/9adc6ccb97ee9556d3f3dac176696c8ddac099bd))


## v1.6.1 (2026-02-02)

### Bug Fixes

- **web**: Wire execution override into WebSocket hook
  ([`82633ea`](https://github.com/inspira-legal/lex-flow/commit/82633ea22b3e30563b096acb9dee0eb912f24d6d))

### Chores

- **web**: Build frontend library [skip ci]
  ([`113565e`](https://github.com/inspira-legal/lex-flow/commit/113565ec0fb59b6e3f0b79b43a69898757b424ed))


## v1.6.0 (2026-02-02)

### Bug Fixes

- **web**: Use composite IDs for node namespacing in visual editor
  ([`fead6b7`](https://github.com/inspira-legal/lex-flow/commit/fead6b790ffc7383eeb799efc17cd90795ad6340))

### Chores

- **web**: Build frontend library [skip ci]
  ([`420135a`](https://github.com/inspira-legal/lex-flow/commit/420135a80f1d6f3ce770b3c204426b0dbddd6398))

### Features

- **web**: Add save button, execution override, and custom opcode URL support
  ([`de6b01a`](https://github.com/inspira-legal/lex-flow/commit/de6b01ae3777dbfe7cc012901531f265dc678c67))


## v1.5.1 (2026-02-01)

### Bug Fixes

- **web**: Properly cleanup WebSocket tasks on disconnect
  ([`fa5e341`](https://github.com/inspira-legal/lex-flow/commit/fa5e3411742154b4c1260ff6239f4db14389c2ed))

### Refactoring

- **web**: Replace context vars with channels for web opcodes
  ([`0ef42d6`](https://github.com/inspira-legal/lex-flow/commit/0ef42d67fec29ed9bdf50cf906da1b9a9eb77426))


## v1.5.0 (2026-01-31)

### Chores

- **web**: Build frontend library [skip ci]
  ([`43ac2c1`](https://github.com/inspira-legal/lex-flow/commit/43ac2c15044fedd5064a5321f1f1d95332796532))

### Features

- **web**: Add extract to workflow feature
  ([`cfa5ee6`](https://github.com/inspira-legal/lex-flow/commit/cfa5ee61c6d60c52fcc07f345fdc25b7842729a7))


## v1.4.0 (2026-01-31)

### Chores

- **web**: Build frontend library [skip ci]
  ([`0096067`](https://github.com/inspira-legal/lex-flow/commit/0096067f1cce018081d9b29999fd9f8bfb9240ab))

### Documentation

- Add README for monorepo and lexflow-web
  ([`a8a5e79`](https://github.com/inspira-legal/lex-flow/commit/a8a5e793dad6ee73f712f49743338af51eaffe32))

- Use uv instead of pip in README examples
  ([`488a5d6`](https://github.com/inspira-legal/lex-flow/commit/488a5d65dd735d411292da1b03a03b78fa3b734d))

### Features

- **web**: Add workflow create/delete and fix start node wiring
  ([`521aec5`](https://github.com/inspira-legal/lex-flow/commit/521aec53feb0740f30b8a268459bd4fccd6439d8))


## v1.3.1 (2026-01-31)

### Bug Fixes

- **web**: Use jsDelivr CDN instead of GitHub release assets
  ([`d4521fa`](https://github.com/inspira-legal/lex-flow/commit/d4521facbaa45e5976d1f5a3c76db166a4918005))

### Chores

- **web**: Build frontend library [skip ci]
  ([`4054ad8`](https://github.com/inspira-legal/lex-flow/commit/4054ad8fc06be0c850feefbbf51fbae73b7fbf67))


## v1.3.0 (2026-01-31)

### Chores

- Add pre-commit hooks for code quality and docs generation
  ([`3d981d4`](https://github.com/inspira-legal/lex-flow/commit/3d981d41ce2b4b214c7d2126ac1889f38ecb1bb0))

- **cli**: Release 1.1.0
  ([`55afa40`](https://github.com/inspira-legal/lex-flow/commit/55afa40d74f37f517f801ff6ceb78558480ee50f))

- **core**: Release 1.1.0
  ([`e91b3dc`](https://github.com/inspira-legal/lex-flow/commit/e91b3dcc6f62de5a3fd0c74947fa4b10dfd6f904))

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

### Features

- **web**: Add embeddable editor library
  ([`9a09f05`](https://github.com/inspira-legal/lex-flow/commit/9a09f054ada301e3527d09a77097de7a5b8ce41d))


## v1.2.0 (2026-01-30)

### Bug Fixes

- **web**: Improve workflow drop target detection
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

### Chores

- Update lock file ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **docs**: Removing unused documentation. ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

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

- **web**: Add redesign documentation ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

### Features

- **web**: Add confirm dialog state management
  ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

- **web**: Add design system foundation ([#6](https://github.com/inspira-legal/lex-flow/pull/6),
  [`7b5a259`](https://github.com/inspira-legal/lex-flow/commit/7b5a25930fc4684b7daa25cfcc49a8122ab577ea))

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


## v1.1.0 (2026-01-29)

### Features

- **web**: Add grammar-driven dynamic node rendering
  ([`37621db`](https://github.com/inspira-legal/lex-flow/commit/37621db67e63cc1b48c4f9fc1ddac62d5575d8f1))


## v1.0.0 (2026-01-29)

- Initial Release
