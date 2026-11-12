--!strict
-- Play-test harness for Maximum Pain (Studio only). In the place it is the ModuleScript
-- ServerStorage.Tools.TestHarness, which never reaches players; this file is the same script.
--
-- Install it once per play session (Test > Play), from the Studio MCP's execute_luau or the
-- command bar:
--   Server:  game.ServerStorage.Tools.TestHarness:Clone().Parent = game.ReplicatedStorage
--   Client:  _G.mp = require(game.ReplicatedStorage:WaitForChild("TestHarness"))
-- The command bar and the MCP run in a Lua VM of their own, so requiring one of the game's
-- modules there gives a fresh copy, not the game's state: the harness reads only instances and
-- attributes. "Stance" is the server's attribute; the hip height shows the client's stance at once.
--
-- mp.start(phases) records the local character every frame until mp.stop():
--   "render"  at the end of the render step, the last code before the frame is drawn. This is what
--             the player sees, including the root moves made in the render step (stance heights,
--             cover, dodge and vault movers).
--   "post"    on PostSimulation, after physics and before the next frame's render step.
--   "both"    (default) each into its own list.
-- Each frame keeps every body part's frame, each held gun's handle, the root's velocity, the hip
-- height, the humanoid's state, the camera, the Stance, TimeScale, Action and HoldMode attributes,
-- and every playing clip by name (weight, time, speed).
--
-- Reports, in studs:
--   mp.floor(opts)          each box's lowest point over the surface under it (negative: in the floor)
--   mp.inside(part, opts)   each box's depth into an obstacle part: the shortest move that would
--                           separate them, and how far it would have to rise to clear it
--   mp.over(part, opts)     how far each box could drop before touching an obstacle while over it
--                           (the clearance over a vaulted top; negative: inside)
--   mp.camera(limit, opts)  frame-to-frame camera height steps larger than `limit`
--   mp.timeline(opts)       stance, state, hip height and the heaviest clips whenever they change
--   mp.clip(name, opts)     a clip's peak weight, and when and how it played
-- opts: { phase = "render" | "post", from = s, to = s, parts = { names }, guns = false } with
-- times in seconds since mp.start(). Boxes are the body parts (not the root) and each gun's box,
-- named by where the gun is ("Right:M9", "Left:AK47"). Depths and clearances are exact box-against-
-- box results (separating axis tests), not sampled points.
-- Driving: mp.look(yaw, pitch), mp.yawTo(point), mp.walk(points), mp.halt(), mp.status(). Keys go
-- through the MCP's keyboard tool; they register with UserInputService:IsKeyDown, which the game reads
-- (aim can be held with the gamepad's ButtonL2). Screenshots: mp.view(eye, at, rootSpace), mp.unview().
-- In Studio play driven by the MCP, the window is usually in the background: frames are drawn at about
-- 15 per second while physics runs at 60, so render-step code (the camera, stances, movers, clip
-- weights) runs in 66 ms steps. Check timing-sensitive results against that.

local CollectionService = game:GetService("CollectionService")
local KeyframeSequenceProvider = game:GetService("KeyframeSequenceProvider")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

export type Track = { name: string, weight: number, time: number, speed: number, length: number }
export type Box = { name: string, frame: CFrame, size: Vector3 }
type Shape = { offset: CFrame, size: Vector3 }
export type Gun = { label: string, handle: CFrame, shape: Shape }
export type Frame = {
    t: number,
    dt: number,
    parts: { [string]: CFrame },
    guns: { Gun },
    velocity: Vector3,
    hip: number,
    state: string,
    grounded: boolean,
    camera: CFrame,
    stance: string,
    scale: number,
    action: string,
    mode: string,
    tracks: { Track },
}
export type Options = { phase: string?, from: number?, to: number?, parts: { string }?, guns: boolean? }

local Harness = {}

local MAX_FRAMES = 4000 -- per list: a minute at 60 fps
local MAX_LINES = 60

Harness.frames = { render = {} :: { Frame }, post = {} :: { Frame } }
Harness.sizes = {} :: { [string]: Vector3 }

local player = Players.LocalPlayer
local clipNames: { [string]: string } = {}
local shapes: { [Model]: Shape } = {}
local started = 0
local recording = false
local postConnection: RBXScriptConnection? = nil
local walkInfo = { active = false, index = 0, count = 0 }

local function short(weaponId: string): string
    return string.match(weaponId, "([^_]+)$") or weaponId
end

local function attribute(instance: Instance, name: string): string
    local value = instance:GetAttribute(name)
    return if value == nil then "" else tostring(value)
end

-- Every clip by the id the game plays it with: its published id (AnimationConfig), or for a clip not
-- published yet its KeyframeSequence's Studio id (a hash of its content, so the id the game registered too).
local function registerClips(): number
    local assets = ReplicatedStorage:FindFirstChild("Assets")
    local folder = assets and assets:FindFirstChild("Animations")
    local count = 0
    for _, sequence in if folder then folder:GetChildren() else {} do
        if sequence:IsA("KeyframeSequence") then
            local ok, id = pcall(function()
                return KeyframeSequenceProvider:RegisterKeyframeSequence(sequence)
            end)
            if ok then
                clipNames[id] = sequence.Name
                count += 1
            end
        end
    end
    local modules = ReplicatedStorage:FindFirstChild("Modules")
    local config = modules and modules:FindFirstChild("AnimationConfig")
    if config and config:IsA("ModuleScript") then
        local ok, loaded = pcall(require, config)
        local slots = if ok and type(loaded) == "table" then (loaded :: any).Slots else nil
        if type(slots) == "table" then
            for _, slot in slots do
                if slot.Id ~= "" then
                    clipNames[slot.Id] = slot.Clip
                end
            end
        end
    end
    return count
end

-- The box round all of a gun's parts, in its Handle's space (measured once per gun, as AimLayer does).
local function shapeOf(gun: Model, handle: BasePart): Shape
    local cached = shapes[gun]
    if cached then
        return cached
    end
    local low, high = Vector3.one * math.huge, -Vector3.one * math.huge
    for _, part in gun:GetDescendants() do
        if part:IsA("BasePart") then
            local frame = handle.CFrame:ToObjectSpace(part.CFrame)
            local half = part.Size / 2
            for _, x in { -1, 1 } do
                for _, y in { -1, 1 } do
                    for _, z in { -1, 1 } do
                        local point = frame:PointToWorldSpace(half * Vector3.new(x, y, z))
                        low, high = low:Min(point), high:Max(point)
                    end
                end
            end
        end
    end
    local shape = { offset = CFrame.new((low + high) / 2), size = high - low }
    shapes[gun] = shape
    return shape
end

local function capture(dt: number): Frame?
    local character = player.Character
    local humanoid = character and character:FindFirstChildOfClass("Humanoid")
    local root = character and character:FindFirstChild("HumanoidRootPart")
    if not character or not humanoid or not root or not root:IsA("BasePart") then
        return nil
    end
    local parts: { [string]: CFrame } = {}
    local guns: { Gun } = {}
    for _, child in character:GetChildren() do
        if child:IsA("BasePart") then
            parts[child.Name] = child.CFrame
            Harness.sizes[child.Name] = child.Size
        elseif child:IsA("Model") and child:GetAttribute("WeaponId") then
            local handle = child:FindFirstChild("Handle")
            if handle and handle:IsA("BasePart") then
                table.insert(guns, {
                    label = attribute(child, "Place") .. ":" .. short(child.Name),
                    handle = handle.CFrame,
                    shape = shapeOf(child, handle),
                })
            end
        end
    end
    local tracks: { Track } = {}
    local animator = humanoid:FindFirstChildOfClass("Animator")
    if animator then
        for _, track in animator:GetPlayingAnimationTracks() do
            local id = if track.Animation then track.Animation.AnimationId else ""
            table.insert(tracks, {
                name = clipNames[id] or id,
                weight = track.WeightCurrent,
                time = track.TimePosition,
                speed = track.Speed,
                length = track.Length,
            })
        end
    end
    local scale = character:GetAttribute("TimeScale")
    return {
        t = os.clock() - started,
        dt = dt,
        parts = parts,
        guns = guns,
        velocity = root.AssemblyLinearVelocity,
        hip = humanoid.HipHeight,
        state = humanoid:GetState().Name,
        grounded = humanoid.FloorMaterial ~= Enum.Material.Air,
        camera = Workspace.CurrentCamera.CFrame,
        stance = attribute(character, "Stance"),
        scale = if typeof(scale) == "number" then scale else 1,
        action = attribute(character, "Action"),
        mode = attribute(character, "HoldMode"),
        tracks = tracks,
    }
end

local function record(list: { Frame }, dt: number)
    if #list < MAX_FRAMES then
        local frame = capture(dt)
        if frame then
            table.insert(list, frame)
        end
    end
end

function Harness.start(phases: string?): string
    Harness.stop()
    table.clear(Harness.frames.render)
    table.clear(Harness.frames.post)
    table.clear(shapes)
    started = os.clock()
    recording = true
    local which = phases or "both"
    if which ~= "post" then
        RunService:BindToRenderStep("mpRecord", Enum.RenderPriority.Last.Value, function(dt: number)
            record(Harness.frames.render, dt)
        end)
    end
    if which ~= "render" then
        postConnection = RunService.PostSimulation:Connect(function(dt: number)
            record(Harness.frames.post, dt)
        end)
    end
    return "recording " .. which
end

function Harness.stop(): string
    if recording then
        pcall(function()
            RunService:UnbindFromRenderStep("mpRecord")
        end)
        if postConnection then
            postConnection:Disconnect()
            postConnection = nil
        end
        recording = false
    end
    local render, post = Harness.frames.render, Harness.frames.post
    local span = if #render > 0 then render[#render].t - render[1].t else 0
    return string.format("render %d frames, post %d frames, %.2f s", #render, #post, span)
end

local function chosen(opts: Options?): { Frame }
    local o = opts or {}
    local list = (Harness.frames :: any)[o.phase or "render"] :: { Frame }
    if not o.from and not o.to then
        return list
    end
    local out = {}
    for _, frame in list do
        if frame.t >= (o.from or -math.huge) and frame.t <= (o.to or math.huge) then
            table.insert(out, frame)
        end
    end
    return out
end

-- The boxes in a frame: the body parts (not the root), then the guns.
function Harness.boxes(frame: Frame, opts: Options?): { Box }
    local o = opts or {}
    local wanted: { [string]: boolean }? = nil
    if o.parts then
        local set = {}
        for _, name in o.parts do
            set[name] = true
        end
        wanted = set
    end
    local out: { Box } = {}
    for name, cframe in frame.parts do
        if name ~= "HumanoidRootPart" and (not wanted or wanted[name]) then
            table.insert(out, { name = name, frame = cframe, size = Harness.sizes[name] })
        end
    end
    if o.guns ~= false then
        for _, gun in frame.guns do
            if not wanted or wanted[gun.label] or wanted.guns then
                table.insert(out, { name = gun.label, frame = gun.handle * gun.shape.offset, size = gun.shape.size })
            end
        end
    end
    return out
end

function Harness.boxOf(part: BasePart): Box
    return { name = part.Name, frame = part.CFrame, size = part.Size }
end

-- The corner of a box furthest down.
function Harness.lowestCorner(frame: CFrame, size: Vector3): Vector3
    local half = size / 2
    local x, y, z = frame.XVector, frame.YVector, frame.ZVector
    return frame.Position
        - x * (if x.Y > 0 then half.X else -half.X)
        - y * (if y.Y > 0 then half.Y else -half.Y)
        - z * (if z.Y > 0 then half.Z else -half.Z)
end

local function axesOf(frame: CFrame): { Vector3 }
    return { frame.XVector, frame.YVector, frame.ZVector }
end

local function radius(axes: { Vector3 }, half: Vector3, axis: Vector3): number
    return math.abs(axes[1]:Dot(axis)) * half.X + math.abs(axes[2]:Dot(axis)) * half.Y + math.abs(axes[3]:Dot(axis)) * half.Z
end

-- The 15 separating axes of two boxes (face normals, then edge crosses).
local function separatingAxes(a: { Vector3 }, b: { Vector3 }): { Vector3 }
    local list = { a[1], a[2], a[3], b[1], b[2], b[3] }
    for _, u in a do
        for _, v in b do
            local cross = u:Cross(v)
            if cross.Magnitude > 1e-6 then
                table.insert(list, cross.Unit)
            end
        end
    end
    return list
end

-- How deep box `a` is inside box `b`: the shortest move that would separate them (0 when apart).
function Harness.penetration(a: Box, b: Box): number
    local aAxes, bAxes = axesOf(a.frame), axesOf(b.frame)
    local offset = b.frame.Position - a.frame.Position
    local depth = math.huge
    for _, axis in separatingAxes(aAxes, bAxes) do
        local overlap = radius(aAxes, a.size / 2, axis) + radius(bAxes, b.size / 2, axis) - math.abs(offset:Dot(axis))
        if overlap <= 0 then
            return 0
        end
        depth = math.min(depth, overlap)
    end
    return depth
end

-- How far box `a` could drop straight down before touching box `b`: negative when they overlap
-- (how far `a` would have to rise to clear `b`), nil when `a` isn't over or under `b` at all.
function Harness.drop(a: Box, b: Box): number?
    local aAxes, bAxes = axesOf(a.frame), axesOf(b.frame)
    local low, high = -math.huge, math.huge
    for _, axis in separatingAxes(aAxes, bAxes) do
        local reach = radius(aAxes, a.size / 2, axis) + radius(bAxes, b.size / 2, axis)
        local gap = (a.frame.Position - b.frame.Position):Dot(axis)
        local k = axis.Y
        if math.abs(k) < 1e-6 then
            if math.abs(gap) > reach then
                return nil
            end
        else
            local t1, t2 = (gap - reach) / k, (gap + reach) / k
            if t1 > t2 then
                t1, t2 = t2, t1
            end
            low, high = math.max(low, t1), math.min(high, t2)
            if low > high then
                return nil
            end
        end
    end
    return if low > -math.huge then low else nil
end

local floorParams = RaycastParams.new()
floorParams.FilterType = Enum.RaycastFilterType.Exclude
floorParams.RespectCanCollide = true

local function refreshFilter()
    local ignore: { Instance } = {}
    for _, other in Players:GetPlayers() do
        if other.Character then
            table.insert(ignore, other.Character)
        end
    end
    for _, model in CollectionService:GetTagged("Combatant") do
        table.insert(ignore, model)
    end
    local dropped = Workspace:FindFirstChild("DroppedWeapons")
    if dropped then
        table.insert(ignore, dropped)
    end
    floorParams.FilterDescendantsInstances = ignore
end

-- The surface under a point, looked for straight down from `fromY`.
function Harness.surfaceUnder(point: Vector3, fromY: number): number?
    local hit = Workspace:Raycast(Vector3.new(point.X, fromY, point.Z), Vector3.new(0, point.Y - fromY - 8, 0), floorParams)
    return if hit then hit.Position.Y else nil
end

type Worst = { value: number, t: number, stance: string, count: number }

local function report(worst: { [string]: Worst }, lowFirst: boolean, format: string): string
    local names = {}
    for name in worst do
        table.insert(names, name)
    end
    table.sort(names, function(a, b)
        return if lowFirst then worst[a].value < worst[b].value else worst[a].value > worst[b].value
    end)
    local lines = {}
    for index, name in names do
        if index > MAX_LINES then
            break
        end
        local entry = worst[name]
        table.insert(lines, string.format(format, name, entry.value, entry.t, entry.stance, entry.count))
    end
    return table.concat(lines, "\n")
end

-- Each box's lowest point over the surface under it: the lowest value, when, and in how many
-- frames it was more than 0.05 under.
function Harness.floor(opts: Options?): string
    refreshFilter()
    local worst: { [string]: Worst } = {}
    local frames = chosen(opts)
    for _, frame in frames do
        local root = frame.parts.HumanoidRootPart
        local rootY = if root then root.Position.Y else 0
        for _, box in Harness.boxes(frame, opts) do
            local corner = Harness.lowestCorner(box.frame, box.size)
            local surface = Harness.surfaceUnder(corner, math.max(corner.Y, rootY) + 1)
            if surface then
                local clearance = corner.Y - surface
                local entry = worst[box.name]
                if not entry then
                    entry = { value = math.huge, t = 0, stance = "", count = 0 }
                    worst[box.name] = entry
                end
                if clearance < entry.value then
                    entry.value, entry.t, entry.stance = clearance, frame.t, frame.stance
                end
                if clearance < -0.05 then
                    entry.count += 1
                end
            end
        end
    end
    return string.format("%d frames\n", #frames) .. report(worst, true, "%-14s lowest %+.2f at %.2f s (%s), %d frames under -0.05")
end

-- Each box's depth into `obstacle` (the shortest separating move) and the most it would have to
-- rise to clear it, over the frames.
function Harness.inside(obstacle: BasePart, opts: Options?): string
    local target = Harness.boxOf(obstacle)
    local deepest: { [string]: Worst } = {}
    local rise: { [string]: Worst } = {}
    local frames = chosen(opts)
    for _, frame in frames do
        for _, box in Harness.boxes(frame, opts) do
            local depth = Harness.penetration(box, target)
            if depth > 0 then
                local entry = deepest[box.name]
                if not entry then
                    entry = { value = 0, t = 0, stance = "", count = 0 }
                    deepest[box.name] = entry
                end
                entry.count += 1
                if depth > entry.value then
                    entry.value, entry.t, entry.stance = depth, frame.t, frame.stance
                end
                local up = Harness.drop(box, target)
                if up and up < 0 then
                    local lift = rise[box.name]
                    if not lift then
                        lift = { value = 0, t = 0, stance = "", count = 0 }
                        rise[box.name] = lift
                    end
                    lift.count += 1
                    if -up > lift.value then
                        lift.value, lift.t, lift.stance = -up, frame.t, frame.stance
                    end
                end
            end
        end
    end
    if next(deepest) == nil then
        return string.format("%d frames: nothing inside %s", #frames, obstacle.Name)
    end
    return string.format("%d frames, inside %s:\n", #frames, obstacle.Name)
        .. report(deepest, false, "%-14s depth %.2f at %.2f s (%s), in %d frames")
        .. "\nwould have to rise:\n"
        .. report(rise, false, "%-14s %.2f at %.2f s (%s), %d frames")
end

-- The clearance over an obstacle while above it: how far each box could drop before touching it.
function Harness.over(obstacle: BasePart, opts: Options?): string
    local target = Harness.boxOf(obstacle)
    local lowest: { [string]: Worst } = {}
    local frames = chosen(opts)
    local overall = math.huge
    local overallName, overallT = "", 0
    for _, frame in frames do
        for _, box in Harness.boxes(frame, opts) do
            local clearance = Harness.drop(box, target)
            if clearance and clearance > -5 then
                local entry = lowest[box.name]
                if not entry then
                    entry = { value = math.huge, t = 0, stance = "", count = 0 }
                    lowest[box.name] = entry
                end
                entry.count += 1
                if clearance < entry.value then
                    entry.value, entry.t, entry.stance = clearance, frame.t, frame.stance
                end
                if clearance < overall then
                    overall, overallName, overallT = clearance, box.name, frame.t
                end
            end
        end
    end
    if next(lowest) == nil then
        return string.format("%d frames: nothing over %s", #frames, obstacle.Name)
    end
    return string.format("%d frames; lowest over %s: %+.2f (%s at %.2f s)\n", #frames, obstacle.Name, overall, overallName, overallT)
        .. report(lowest, true, "%-14s %+.2f at %.2f s (%s), over it in %d frames")
end

-- Frame-to-frame camera height steps larger than `limit`, and the largest.
function Harness.camera(limit: number?, opts: Options?): string
    local frames = chosen(opts)
    local lines = {}
    local largest, at = 0, 0
    for index = 2, #frames do
        local step = frames[index].camera.Position.Y - frames[index - 1].camera.Position.Y
        if math.abs(step) > largest then
            largest, at = math.abs(step), frames[index].t
        end
        if math.abs(step) > (limit or 0.5) and #lines < MAX_LINES then
            table.insert(lines, string.format("%.2f s: %+.2f (%s)", frames[index].t, step, frames[index].stance))
        end
    end
    return string.format("%d frames; largest camera step %.2f at %.2f s\n", #frames, largest, at) .. table.concat(lines, "\n")
end

local function heaviest(frame: Frame, count: number): string
    local tracks = table.clone(frame.tracks)
    table.sort(tracks, function(a, b)
        return a.weight > b.weight
    end)
    local names = {}
    for index, track in tracks do
        if index > count or track.weight < 0.1 then
            break
        end
        table.insert(names, string.format("%s %.2f", track.name, track.weight))
    end
    return table.concat(names, ", ")
end

-- The stance, humanoid state, hip height and heaviest clips whenever any of them changes.
function Harness.timeline(opts: Options?): string
    local lines = {}
    local last = ""
    for _, frame in chosen(opts) do
        local clips = heaviest(frame, 3)
        local names = string.gsub(clips, " [%d%.]+", "")
        local key = string.format("%s|%s|%.1f|%s", frame.stance, frame.state, frame.hip, names)
        if key ~= last and #lines < MAX_LINES then
            last = key
            table.insert(lines, string.format("%.2f s  %s  %s  hip %.2f  %s", frame.t, frame.stance, frame.state, frame.hip, clips))
        end
    end
    return table.concat(lines, "\n")
end

-- A clip's peak weight, when it played, and its time and speed ranges.
function Harness.clip(name: string, opts: Options?): string
    local peak, peakT = 0, 0
    local first, last: number? = nil, nil
    local lowTime, highTime, lowSpeed, highSpeed = math.huge, -math.huge, math.huge, -math.huge
    for _, frame in chosen(opts) do
        for _, track in frame.tracks do
            if track.name == name and track.weight > 0.01 then
                first = first or frame.t
                last = frame.t
                if track.weight > peak then
                    peak, peakT = track.weight, frame.t
                end
                lowTime, highTime = math.min(lowTime, track.time), math.max(highTime, track.time)
                lowSpeed, highSpeed = math.min(lowSpeed, track.speed), math.max(highSpeed, track.speed)
            end
        end
    end
    if not first then
        return name .. ": not played"
    end
    return string.format(
        "%s: peak %.2f at %.2f s; from %.2f to %.2f s; time %.2f to %.2f; speed %.2f to %.2f",
        name,
        peak,
        peakT,
        first,
        last :: number,
        lowTime,
        highTime,
        lowSpeed,
        highSpeed
    )
end

-- Points the camera (radians; yaw pi faces +Z). The game only reacts when the value changes.
function Harness.look(yaw: number, pitch: number?)
    local value = Vector2.new(yaw, pitch or 0)
    if player:GetAttribute("DebugLook") == value then
        value += Vector2.new(1e-4, 0)
    end
    player:SetAttribute("DebugLook", value)
end

-- The camera yaw that faces `point` from the character.
function Harness.yawTo(point: Vector3): number
    local character = player.Character
    local root = character and character:FindFirstChild("HumanoidRootPart")
    if not root or not root:IsA("BasePart") then
        return 0
    end
    local offset = point - root.Position
    return math.atan2(-offset.X, -offset.Z)
end

-- Walks through `points` (world positions; only X and Z count), after Roblox's control script each
-- frame, so it wins. Don't walk in cover: the cover mover's own steps would be overridden.
function Harness.walk(points: { Vector3 }, tolerance: number?)
    Harness.halt()
    walkInfo = { active = true, index = 1, count = #points }
    RunService:BindToRenderStep("mpWalk", Enum.RenderPriority.Camera.Value + 20, function()
        local character = player.Character
        local humanoid = character and character:FindFirstChildOfClass("Humanoid")
        local root = character and character:FindFirstChild("HumanoidRootPart")
        if not humanoid or not root or not root:IsA("BasePart") then
            return
        end
        local target = points[walkInfo.index]
        if not target then
            humanoid:Move(Vector3.zero, false)
            Harness.halt()
            return
        end
        local offset = Vector3.new(target.X - root.Position.X, 0, target.Z - root.Position.Z)
        if offset.Magnitude < (tolerance or 0.5) then
            walkInfo.index += 1
        else
            humanoid:Move(offset.Unit, false)
        end
    end)
end

function Harness.halt()
    pcall(function()
        RunService:UnbindFromRenderStep("mpWalk")
    end)
    walkInfo.active = false
end

-- A debug camera for screenshots: the frame is drawn from `eye` looking at `at` (world positions, or
-- offsets in the root's space when `rootSpace` is true), and the game's own camera is put back on
-- PreAnimation, before anything reads it (the aim layer aims from it). Recordings made while it is
-- on log the debug camera.
local viewRestore: RBXScriptConnection? = nil
function Harness.view(eye: Vector3, at: Vector3, rootSpace: boolean?)
    Harness.unview()
    local saved: CFrame? = nil
    RunService:BindToRenderStep("mpView", Enum.RenderPriority.Last.Value - 1, function()
        local camera = Workspace.CurrentCamera
        local character = player.Character
        local root = character and character:FindFirstChild("HumanoidRootPart")
        local from, to = eye, at
        if rootSpace and root and root:IsA("BasePart") then
            from, to = root.CFrame:PointToWorldSpace(eye), root.CFrame:PointToWorldSpace(at)
        end
        saved = camera.CFrame
        camera.CFrame = CFrame.lookAt(from, to)
    end)
    viewRestore = RunService.PreAnimation:Connect(function()
        if saved then
            Workspace.CurrentCamera.CFrame = saved
            saved = nil
        end
    end)
end

function Harness.unview()
    pcall(function()
        RunService:UnbindFromRenderStep("mpView")
    end)
    if viewRestore then
        viewRestore:Disconnect()
        viewRestore = nil
    end
end

function Harness.walking(): boolean
    return walkInfo.active
end

function Harness.status(): string
    local character = player.Character
    local humanoid = character and character:FindFirstChildOfClass("Humanoid")
    local root = character and character:FindFirstChild("HumanoidRootPart")
    if not character or not humanoid or not root or not root:IsA("BasePart") then
        return "no character"
    end
    local guns = {}
    for _, child in character:GetChildren() do
        if child:IsA("Model") and child:GetAttribute("WeaponId") then
            table.insert(guns, attribute(child, "Place") .. ":" .. short(child.Name))
        end
    end
    local p = root.Position
    return string.format(
        "root (%.2f, %.2f, %.2f) stance %s hip %.2f state %s mode %s guns %s painkillers %s adrenaline %s timescale %s",
        p.X,
        p.Y,
        p.Z,
        attribute(character, "Stance"),
        humanoid.HipHeight,
        humanoid:GetState().Name,
        attribute(character, "HoldMode"),
        table.concat(guns, " "),
        attribute(character, "Painkillers"),
        attribute(character, "Adrenaline"),
        attribute(character, "TimeScale")
    )
end

Harness.clips = registerClips()

return Harness
