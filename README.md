# Digital Human Twin

Minimal C++/Qt base for a future digital human twin application.

## Goal

- Start with a clean desktop architecture
- Keep the codebase small
- Add future features inside `src/modules`

## Tech

- C++17
- Qt 6 Widgets
- CMake

## Structure

```text
src/
  app/
  core/
  modules/
```

## Build

Qt 6 must be installed first.

```bash
cmake -S . -B build
cmake --build build
```
