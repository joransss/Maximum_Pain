--!strict
-- Studio edit mode (command bar or MCP): builds a KeyframeSequence per clip in
-- ReplicatedStorage.Assets.Animations from the keyframes Blender serves (mp_serve.py, which serves
-- Exports/keyframes.json at http://127.0.0.1:8765). HTTP is switched on only for the fetch.
-- Each track holds only the keys Blender kept (sparse keyframes); a joint a clip doesn't animate has
-- no poses at all, so lower-priority animations keep it. Parents are added with Weight 0 so the
-- pose hierarchy stays intact. Re-importing replaces clips of the same name.

local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local URL = "http://127.0.0.1:8765/keyframes.json"
local PARENT: { [string]: string } = {
    LowerTorso = "HumanoidRootPart",
    UpperTorso = "LowerTorso",
    Head = "UpperTorso",
    RightUpperArm = "UpperTorso",
    RightLowerArm = "RightUpperArm",
    RightHand = "RightLowerArm",
    LeftUpperArm = "UpperTorso",
    LeftLowerArm = "LeftUpperArm",
    LeftHand = "LeftLowerArm",
    RightUpperLeg = "LowerTorso",
    RightLowerLeg = "RightUpperLeg",
    RightFoot = "RightLowerLeg",
    LeftUpperLeg = "LowerTorso",
    LeftLowerLeg = "LeftUpperLeg",
    LeftFoot = "LeftLowerLeg",
}

local was = HttpService.HttpEnabled
HttpService.HttpEnabled = true
local ok, body = pcall(HttpService.GetAsync, HttpService, URL, true)
HttpService.HttpEnabled = was
assert(ok, body)
local clips = HttpService:JSONDecode(body :: string)

local assets = ReplicatedStorage:WaitForChild("Assets")
local folder = assets:FindFirstChild("Animations")
if not folder then
    folder = Instance.new("Folder")
    folder.Name = "Animations"
    folder.Parent = assets
end

local names = {}
for _, clip in clips do
    local sequence = Instance.new("KeyframeSequence")
    sequence.Name = clip.name
    sequence.Loop = clip.loop
    sequence.Priority = (Enum.AnimationPriority :: any)[clip.priority]
    -- Every time any track has a key, with that track's pose.
    local byTime: { [number]: { [string]: CFrame } } = {}
    for poseName, rows in clip.tracks do
        for _, row in rows do
            local time = row[1]
            byTime[time] = byTime[time] or {}
            local q = { w = row[5], x = row[6], y = row[7], z = row[8] }
            -- CFrame.new(x, y, z, qx, qy, qz, qw)
            byTime[time][poseName] = CFrame.new(row[2], row[3], row[4], q.x, q.y, q.z, q.w)
        end
    end
    -- The clip's length is its last keyframe; make sure one sits exactly there.
    if not byTime[clip.length] then
        byTime[clip.length] = {}
    end
    local times = {}
    for time in byTime do
        table.insert(times, time)
    end
    table.sort(times)
    for _, time in times do
        local keyframe = Instance.new("Keyframe")
        keyframe.Time = time
        local poses: { [string]: Pose } = {}
        local function pose(name: string): Pose
            local existing = poses[name]
            if existing then
                return existing
            end
            local created = Instance.new("Pose")
            created.Name = name
            created.Weight = 0
            created.EasingStyle = Enum.PoseEasingStyle.Linear -- sampled from Blender; the easing is in the samples
            local parentName = PARENT[name]
            if parentName then
                created.Parent = pose(parentName)
            end
            poses[name] = created
            return created
        end
        pose("HumanoidRootPart").Parent = keyframe
        for poseName, cframe in byTime[time] do
            local p = pose(poseName)
            p.Weight = 1
            p.CFrame = cframe
        end
        keyframe.Parent = sequence
    end
    for _, marker in clip.markers do
        local keyframe: Keyframe? = nil
        for _, child in sequence:GetChildren() do
            if child:IsA("Keyframe") and math.abs(child.Time - marker[1]) < 1e-3 then
                keyframe = child
            end
        end
        if not keyframe then
            keyframe = Instance.new("Keyframe")
            keyframe.Time = marker[1]
            local root = Instance.new("Pose")
            root.Name = "HumanoidRootPart"
            root.Weight = 0
            root.Parent = keyframe
            keyframe.Parent = sequence
        end
        local m = Instance.new("KeyframeMarker")
        m.Name = marker[2]
        m.Value = tostring(marker[3] or "")
        m.Parent = keyframe
    end
    local old = folder:FindFirstChild(clip.name)
    if old then
        old:Destroy()
    end
    sequence.Parent = folder
    table.insert(names, clip.name)
    task.wait()
end
return ("imported %d clips: %s"):format(#names, table.concat(names, ", "))
