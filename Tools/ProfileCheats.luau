--!strict
-- Studio-only cheats for play tests: set your own Level, XP, Cash and Prestige, or start your profile
-- afresh. Never part of a live game: it lives in ServerStorage.Tools, where scripts don't run, and stops
-- at once outside Studio. The repo has the same script as Tools/ProfileCheats.luau.
--
-- Install it once per play session, on the server (the Studio MCP's execute_luau, or the command bar
-- in the server's view):
--   game.ServerStorage.Tools.ProfileCheats:Clone().Parent = game.ServerScriptService
-- Cloned there it runs as one of the game's scripts, so it changes the profiles the game holds (a
-- `require` from the command bar would get a copy of ProfileService of its own). It adds the
-- RemoteFunction ReplicatedStorage.Remotes.DebugProfile, which the test harness calls from the client:
--   mp.profile({ Level = 20, Cash = 5000, Prestige = 1 })  -- XP goes back to 0 with a new level
--   mp.profile({ XP = 150 })
--   mp.profile({ Reset = true })                           -- a new player's profile
--   mp.profile()                                           -- what the profile holds now
-- Each change goes through ProfileService.update like any other, so it is checked (level 1 to 50,
-- prestige 0 to 5, whole numbers) and saved like any other (to the Studio DataStore).

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local ServerScriptService = game:GetService("ServerScriptService")

if not RunService:IsStudio() then
    return
end

local ProfileSchema = require(ServerScriptService:WaitForChild("ProfileSchema"))
local ProfileService = require(ServerScriptService:WaitForChild("ProfileService"))

local FIELDS: { [string]: boolean } = { Level = true, XP = true, Cash = true, Prestige = true }

local remotes = ReplicatedStorage:WaitForChild("Remotes")
local old = remotes:FindFirstChild("DebugProfile")
if old then
    old:Destroy() -- installed twice in one session
end
local remote = Instance.new("RemoteFunction")
remote.Name = "DebugProfile"
remote.Parent = remotes

local function describe(player: Player): string
    local profile = ProfileService.get(player)
    if not profile then
        return "no profile is loaded for " .. player.Name
    end
    local where = if player:GetAttribute("ProfileOffline") then " (kept in memory only: Studio can't reach DataStores)" else ""
    return `Level {profile.Level}, XP {profile.XP}, Cash ${profile.Cash}, Prestige {profile.Prestige}{where}`
end

remote.OnServerInvoke = function(player: Player, request: unknown): string
    local wanted: { [string]: number } = {}
    local reset = false
    if request ~= nil then
        if type(request) ~= "table" then
            return "send a table, like { Level = 20 }"
        end
        for key, value in request :: { [any]: any } do
            if key == "Reset" then
                if value ~= true then
                    return "Reset must be true"
                end
                reset = true
            elseif type(key) ~= "string" or not FIELDS[key] then
                return `{tostring(key)} can't be set (only Level, XP, Cash, Prestige and Reset)`
            elseif type(value) ~= "number" then
                return `{key} must be a number`
            else
                wanted[key] = value
            end
        end
    end
    if reset or next(wanted) ~= nil then
        local ok, problem = ProfileService.update(player, function(profile)
            if reset then
                for key in profile :: any do
                    (profile :: any)[key] = nil
                end
                for key, value in ProfileSchema.new() :: any do
                    (profile :: any)[key] = value
                end
            end
            if wanted.Level then
                profile.XP = 0 -- a new level starts with no XP towards the next, unless XP is set too
            end
            for key, value in wanted do
                (profile :: any)[key] = value
            end
        end)
        if not ok then
            return `refused: {problem}`
        end
    end
    return describe(player)
end

print("ProfileCheats: ready (ReplicatedStorage.Remotes.DebugProfile)")
