-- Studio command-bar / MCP import: builds KeyframeSequences in ReplicatedStorage.Animations from clips.json.
-- In Blender: run mp_rig.py (or open MP_R15_Animations.blend), mp_clips.py, mp_export.py (writes export/clips.json),
-- then mp_serve.py (serves export/ at http://127.0.0.1:8765). HTTP is enabled only for the fetch, then restored.
-- Re-importing replaces clips of the same name; republish changed clips and update Shared.AnimationIds.
-- Joints a clip doesn't animate are left out; their parents are kept with Weight 0 for the Pose hierarchy.
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local URL = "http://127.0.0.1:8765/clips.json"

local PARENT = {
	LowerTorso = "HumanoidRootPart", UpperTorso = "LowerTorso", Head = "UpperTorso",
	RightUpperArm = "UpperTorso", RightLowerArm = "RightUpperArm", RightHand = "RightLowerArm",
	LeftUpperArm = "UpperTorso", LeftLowerArm = "LeftUpperArm", LeftHand = "LeftLowerArm",
	RightUpperLeg = "LowerTorso", RightLowerLeg = "RightUpperLeg", RightFoot = "RightLowerLeg",
	LeftUpperLeg = "LowerTorso", LeftLowerLeg = "LeftUpperLeg", LeftFoot = "LeftLowerLeg",
}

local was = HttpService.HttpEnabled
HttpService.HttpEnabled = true
local ok, body = pcall(HttpService.GetAsync, HttpService, URL, true)
HttpService.HttpEnabled = was
assert(ok, body)
local clips = HttpService:JSONDecode(body)

local folder = ReplicatedStorage:FindFirstChild("Animations")
if not folder then
	folder = Instance.new("Folder")
	folder.Name = "Animations"
	folder.Parent = ReplicatedStorage
end

local names = {}
for _, clip in clips do
	local ks = Instance.new("KeyframeSequence")
	ks.Name = clip.name
	ks.Loop = clip.loop
	ks.Priority = Enum.AnimationPriority[clip.priority]
	for _, frame in clip.frames do
		local kf = Instance.new("Keyframe")
		kf.Time = frame[1]
		local poses = {}
		local function pose(name)
			if poses[name] then return poses[name] end
			local p = Instance.new("Pose")
			p.Name = name
			p.Weight = 0
			p.EasingStyle = Enum.PoseEasingStyle.Linear -- baked at 30 fps; Blender already eased between keys
			if PARENT[name] then p.Parent = pose(PARENT[name]) end
			poses[name] = p
			return p
		end
		local v = frame[2]
		for i, joint in clip.joints do
			local o = (i - 1) * 7
			local p = pose(joint)
			p.Weight = 1
			p.CFrame = CFrame.new(v[o + 1], v[o + 2], v[o + 3], v[o + 4], v[o + 5], v[o + 6], v[o + 7])
		end
		poses.HumanoidRootPart.Parent = kf
		kf.Parent = ks
	end
	local old = folder:FindFirstChild(clip.name)
	if old then old:Destroy() end
	ks.Parent = folder
	table.insert(names, clip.name)
	task.wait()
end
return ("imported %d clips: %s"):format(#names, table.concat(names, ", "))
