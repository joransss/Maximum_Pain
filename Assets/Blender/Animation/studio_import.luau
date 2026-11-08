--!strict
-- Studio-only tool (edit mode): builds a KeyframeSequence per clip in ReplicatedStorage.Assets.Animations
-- from the keyframes Blender serves (Assets/Blender/Animation/mp_serve.py serves Exports/keyframes.json at
-- http://127.0.0.1:8765). The same code as studio_import.luau in the repo. Command bar:
--     require(game.ServerStorage.Tools.AnimationImporter:Clone())()
-- Each track holds only the keys Blender kept (sparse keyframes); a joint a clip doesn't animate has
-- no poses at all, so lower-priority animations keep it. Parents get Weight 0 so the pose hierarchy
-- stays intact. Re-importing replaces clips of the same name. HTTP is on only for the fetch.

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

local function build(clip: any): KeyframeSequence
    local sequence = Instance.new("KeyframeSequence")
    sequence.Name = clip.name
    sequence.Loop = clip.loop
    sequence.Priority = (Enum.AnimationPriority :: any)[clip.priority]
    local byTime: { [number]: { [string]: CFrame } } = {}
    for poseName, rows in clip.tracks do
        for _, row in rows do
            local time = row[1]
            byTime[time] = byTime[time] or {}
            -- rows are [time, x, y, z, qw, qx, qy, qz]; CFrame.new takes (x, y, z, qx, qy, qz, qw)
            byTime[time][poseName] = CFrame.new(row[2], row[3], row[4], row[6], row[7], row[8], row[5])
        end
    end
    byTime[clip.length] = byTime[clip.length] or {}
    local times = {}
    for time in byTime do
        table.insert(times, time)
    end
    table.sort(times)
    local keyframes: { [number]: Keyframe } = {}
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
            created.EasingStyle = Enum.PoseEasingStyle.Linear -- sampled in Blender; the easing is in the samples
            local parentName = PARENT[name]
            if parentName then
                created.Parent = pose(parentName)
            end
            poses[name] = created
            return created
        end
        pose("HumanoidRootPart").Parent = keyframe
        for poseName, cframe in byTime[time] do
            local found = pose(poseName)
            found.Weight = 1
            found.CFrame = cframe
        end
        keyframe.Parent = sequence
        keyframes[time] = keyframe
    end
    for _, marker in clip.markers do
        local keyframe = keyframes[marker[1]]
        if not keyframe then
            local created = Instance.new("Keyframe")
            created.Time = marker[1]
            local root = Instance.new("Pose")
            root.Name = "HumanoidRootPart"
            root.Weight = 0
            root.Parent = created
            created.Parent = sequence
            keyframes[marker[1]] = created
            keyframe = created
        end
        local tag = Instance.new("KeyframeMarker")
        tag.Name = marker[2]
        tag.Value = tostring(marker[3] or "")
        tag.Parent = keyframe
    end
    return sequence
end

return function(): string
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
        local sequence = build(clip)
        local old = (folder :: Instance):FindFirstChild(clip.name)
        if old then
            old:Destroy()
        end
        sequence.Parent = folder
        table.insert(names, clip.name)
        task.wait()
    end
    return ("imported %d clips: %s"):format(#names, table.concat(names, ", "))
end
