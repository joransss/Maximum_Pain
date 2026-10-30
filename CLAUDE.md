# Roblox Full-Stack Game Development Guide (Coding, Modeling & Animation)

## 1. Project Architecture & Standards
- Environment: Luau (Roblox dialect) with modern strict typing (`--!strict`).
- Tooling & Formatting:
  - Format all Luau code according to StyLua standards (4-space indentation, explicit line endings).
  - Code managed via Rojo sync or direct Roblox Studio MCP execution.
- Workspace Organization:
  - Game logic split logically across `ServerScriptService`, `ReplicatedStorage.Modules`, and `StarterPlayer.StarterPlayerScripts`.
  - Assets organized under `ReplicatedStorage.Assets` (`Models`, `Animations`, `Sounds`, `UI`).
- Roblox Scale Rules:
  - 1 Roblox Stud = 0.28 meters.
  - Standard R15 Avatar Height = 5 Studs (~1.4 meters / ~5 Blender Units).

---

## 2. Code Formatting, Style & Reusability Rules

### Naming Conventions & Typing
- Language Level: Enforce `--!strict` at the top of every Luau file.
- Naming Standards:
  - Instances & Roblox Services: `PascalCase` (e.g., `game:GetService("Players")`, `Workspace.Baseplate`).
  - Variables & Functions: `camelCase` (e.g., `local playerHealth = 100`, `function calculateDamage()`).
  - Constants & Enums: `ALL_CAPS_SNAKE` (e.g., `local MAX_RETRIES = 3`).
  - Custom Types / Interfaces: `PascalCase` (e.g., `type WeaponData = { Damage: number, FireRate: number }`).

### Modularity & Reusability
- ModuleScript Architecture: Keep scripts single-responsibility. Prefer clean object-oriented or functional `ModuleScripts` over giant monolithic scripts.
- Memory & Event Lifecycle:
  - Always disconnect `RBXScriptConnection` instances when no longer needed, or use a cleanup manager (`Maid` / `Janitor` pattern).
  - Use `task.cancel()` for pending thread tasks.
- API Lifetime Practices:
  - Use `task.wait()`, `task.spawn()`, and `task.defer()` instead of legacy `wait()` or `coroutine`.
  - Wrap DataStore calls (`UpdateAsync`/`GetAsync`) and external network requests in `pcall`.

### Security & Authority
- Client/Server Division:
  - Server handles DataStores, combat validation, hit detection authority, inventory, and economy.
  - Client handles camera, local UI, input (`UserInputService`/`ContextActionService`), local audio, and visual FX.
  - NEVER trust client input. Validate all parameters received on `RemoteEvent` / `RemoteFunction` endpoints.

---

## 3. Blender 3D Modeling Rules (Blender MCP)
- Mesh Budget & Optimization:
  - Keep low-poly weapon/prop meshes under 2,500 triangles per asset.
  - Apply transform (`Scale = 1.0`, `Rotation = 0,0,0`) before exporting FBX files.
  - Merge duplicate vertices and clear custom split normals before export.
- Hierarchy & Naming Conventions:
  - Use clear prefixes: `GEO_` for meshes, `RIG_` for armatures, `MAT_` for materials.
  - Set the Mesh Origin (Pivot) at the exact grip/handle point where the R15 `RightHand` Motor6D attaches.
- Component Sub-Parts & Attachments:
  - Separate interactive mesh parts (e.g., `Magazine`, `Slide`, `PumpHandle`) for reload animations.
  - Include specific named attachments or bones:
    - `Handle`: Base attachment point for character welding.
    - `Muzzle`: Attachment point for particle emitters and sound cues.

---

## 4. Animation & Motion Rules
- Rigging & Loaders:
  - Load animations exclusively through the `Animator` instance (`Humanoid.Animator` or `AnimationController.Animator`).
  - NEVER use deprecated `Humanoid:LoadAnimation()`.
- Track Priorities:
  - Explicitly assign `AnimationPriority`:
    - `Enum.AnimationPriority.Core`: Base/Idle pose
    - `Enum.AnimationPriority.Movement`: Walk / Run / Strafe
    - `Enum.AnimationPriority.Action`: Combat swings, reload, weapon draws
- Event Synchronization (Animation Markers):
  - Sync hitboxes, VFX, and audio signals using Animation Markers (`Track:GetMarkerReachedSignal("MarkerName")`).
  - Server verifies damage hits; client triggers cosmetic particle bursts and audio playback on marker signals.

---

## 5. Toolchain & MCP Workflow Guidelines

### Roblox Studio MCP
- Use `run_code` / `execute_luau` for building scene instances and running validation tests.
- Use `get_script_source` and `grep_scripts` to inspect existing project logic before editing.
- Always write formatted, typed Luau code when generating new ModuleScripts or components.

### Blender MCP
- Execute Python commands (`bpy`) to programmatically build, rig, and UV-unwrap geometry.
- Automatically group objects into collections (`Pistols`, `Rifles`, `Environment`).
- Export assets to `.fbx` with FBX unit scaling set to `1.0`.