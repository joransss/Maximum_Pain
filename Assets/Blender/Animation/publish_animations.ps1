# Publishes the game's animations to Roblox through Open Cloud, since Studio can't do it in bulk
# (AssetService:CreateAssetAsync says "not available yet").
#
#   -Build   writes Exports/rbxmx/<clip>.rbxmx for every clip in Exports/keyframes.json, built the same
#            way studio_import.luau builds the KeyframeSequences in the place.
#   -Upload  uploads each built clip that isn't in Exports/animation_ids.json yet and records its id
#            there after each success, so a run that stops can simply be started again.
#   -Only    limits either step to the named clips. -Force re-uploads clips that already have an id
#            (for a clip changed in Blender).
#
# The API key is read from the ROBLOX_API_KEY environment variable. It must be an Open Cloud key made on
# the account that owns the place (83tg), with Assets read and write. Example:
#   powershell -ExecutionPolicy Bypass -File publish_animations.ps1 -Build
#   powershell -ExecutionPolicy Bypass -File publish_animations.ps1 -Upload -Only AimPistol

param(
    [switch]$Build,
    [switch]$Upload,
    [string[]]$Only,
    [switch]$Force,
    [string]$UserId = "861789897" # 83tg
)

$ErrorActionPreference = "Stop"
$Invariant = [System.Globalization.CultureInfo]::InvariantCulture
$Exports = Join-Path $PSScriptRoot "Exports"
$OutDir = Join-Path $Exports "rbxmx"
$IdsFile = Join-Path $Exports "animation_ids.json"

$Parent = @{
    LowerTorso = "HumanoidRootPart"; UpperTorso = "LowerTorso"; Head = "UpperTorso"
    RightUpperArm = "UpperTorso"; RightLowerArm = "RightUpperArm"; RightHand = "RightLowerArm"
    LeftUpperArm = "UpperTorso"; LeftLowerArm = "LeftUpperArm"; LeftHand = "LeftLowerArm"
    RightUpperLeg = "LowerTorso"; RightLowerLeg = "RightUpperLeg"; RightFoot = "RightLowerLeg"
    LeftUpperLeg = "LowerTorso"; LeftLowerLeg = "LeftUpperLeg"; LeftFoot = "LeftLowerLeg"
}
$Priority = @{ Idle = 0; Movement = 1; Action = 2; Action2 = 3; Action3 = 4; Action4 = 5; Core = 1000 }

# JSON numbers arrive as Int32 or Decimal; going through their text gives the same double Luau reads.
function Num($value) { [double]::Parse(([string]::Format($Invariant, "{0}", $value)), $Invariant) }
function F([double]$value) { $value.ToString("R", $Invariant) }
function Esc([string]$text) { [System.Security.SecurityElement]::Escape($text) }

function Write-Clip($clip) {
    $script:ref = 0
    function NextRef { $script:ref++; "RBX$script:ref" }

    # Keyframes by time: pose name -> [x, y, z, qw, qx, qy, qz]; one at the clip's length too.
    $byTime = @{}
    foreach ($track in $clip.tracks.PSObject.Properties) {
        foreach ($row in $track.Value) {
            $t = Num $row[0]
            if (-not $byTime.ContainsKey($t)) { $byTime[$t] = @{} }
            $byTime[$t][$track.Name] = @($row | ForEach-Object { Num $_ })
        }
    }
    $length = Num $clip.length
    if (-not $byTime.ContainsKey($length)) { $byTime[$length] = @{} }
    $markers = @{}
    foreach ($marker in $clip.markers) {
        $t = Num $marker[0]
        if (-not $markers.ContainsKey($t)) { $markers[$t] = @() }
        $value = if ($marker.Count -gt 2 -and $null -ne $marker[2]) { [string]::Format($Invariant, "{0}", $marker[2]) } else { "" }
        $markers[$t] += , @($marker[1], $value)
        if (-not $byTime.ContainsKey($t)) { $byTime[$t] = $null } # a marker-only keyframe: root pose only
    }

    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append('<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">')
    [void]$sb.Append('<External>null</External><External>nil</External>')
    [void]$sb.Append("<Item class=`"KeyframeSequence`" referent=`"$(NextRef)`"><Properties>")
    [void]$sb.Append("<bool name=`"Loop`">$(([string]$clip.loop).ToLower())</bool>")
    [void]$sb.Append("<string name=`"Name`">$(Esc $clip.name)</string>")
    [void]$sb.Append("<token name=`"Priority`">$($Priority[[string]$clip.priority])</token>")
    [void]$sb.Append("</Properties>")

    foreach ($t in ($byTime.Keys | Sort-Object)) {
        [void]$sb.Append("<Item class=`"Keyframe`" referent=`"$(NextRef)`"><Properties>")
        [void]$sb.Append("<string name=`"Name`">Keyframe</string><float name=`"Time`">$(F $t)</float></Properties>")
        $keys = $byTime[$t]
        if ($null -eq $keys) { $keys = @{} }

        # Every keyed joint plus its parents up to the root; parents that aren't keyed get Weight 0.
        $needed = @{ HumanoidRootPart = $true }
        foreach ($name in $keys.Keys) {
            $n = $name
            while ($n) { $needed[$n] = $true; $n = $Parent[$n] }
        }
        $children = @{}
        foreach ($name in $needed.Keys) {
            $p = $Parent[$name]
            if ($p) {
                if (-not $children.ContainsKey($p)) { $children[$p] = @() }
                $children[$p] += $name
            }
        }
        $writePose = $null
        $writePose = {
            param($name)
            $row = $keys[$name]
            if ($row) {
                $x, $y, $z, $qw, $qx, $qy, $qz = $row[1..7]
                $len = [math]::Sqrt($qw * $qw + $qx * $qx + $qy * $qy + $qz * $qz)
                $qw /= $len; $qx /= $len; $qy /= $len; $qz /= $len
                $m = @(
                    (1 - 2 * ($qy * $qy + $qz * $qz)), (2 * ($qx * $qy - $qw * $qz)), (2 * ($qx * $qz + $qw * $qy)),
                    (2 * ($qx * $qy + $qw * $qz)), (1 - 2 * ($qx * $qx + $qz * $qz)), (2 * ($qy * $qz - $qw * $qx)),
                    (2 * ($qx * $qz - $qw * $qy)), (2 * ($qy * $qz + $qw * $qx)), (1 - 2 * ($qx * $qx + $qy * $qy))
                )
                $weight = 1
            } else {
                $x = $y = $z = 0.0
                $m = @(1, 0, 0, 0, 1, 0, 0, 0, 1)
                $weight = 0
            }
            [void]$sb.Append("<Item class=`"Pose`" referent=`"$(NextRef)`"><Properties><CoordinateFrame name=`"CFrame`">")
            [void]$sb.Append("<X>$(F $x)</X><Y>$(F $y)</Y><Z>$(F $z)</Z>")
            $labels = "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22"
            for ($i = 0; $i -lt 9; $i++) { [void]$sb.Append("<$($labels[$i])>$(F $m[$i])</$($labels[$i])>") }
            [void]$sb.Append("</CoordinateFrame><token name=`"EasingDirection`">0</token><token name=`"EasingStyle`">0</token>")
            [void]$sb.Append("<string name=`"Name`">$name</string><float name=`"Weight`">$weight</float></Properties>")
            foreach ($child in ($children[$name] | Sort-Object)) { & $writePose $child }
            [void]$sb.Append("</Item>")
        }
        & $writePose "HumanoidRootPart"

        if ($markers.ContainsKey($t)) {
            foreach ($marker in $markers[$t]) {
                [void]$sb.Append("<Item class=`"KeyframeMarker`" referent=`"$(NextRef)`"><Properties>")
                [void]$sb.Append("<string name=`"Name`">$(Esc $marker[0])</string><string name=`"Value`">$(Esc $marker[1])</string></Properties></Item>")
            }
        }
        [void]$sb.Append("</Item>")
    }
    [void]$sb.Append("</Item></roblox>")
    [System.IO.File]::WriteAllText((Join-Path $OutDir "$($clip.name).rbxmx"), $sb.ToString(), (New-Object System.Text.UTF8Encoding $false))
}

function Load-Ids {
    $ids = [ordered]@{}
    if (Test-Path $IdsFile) {
        (Get-Content $IdsFile -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $ids[$_.Name] = [string]$_.Value }
    }
    $ids
}

function Save-Ids($ids) {
    $sorted = [ordered]@{}
    foreach ($k in ($ids.Keys | Sort-Object)) { $sorted[$k] = $ids[$k] }
    [System.IO.File]::WriteAllText($IdsFile, ($sorted | ConvertTo-Json), (New-Object System.Text.UTF8Encoding $false))
}

function Send-Clip($client, [string]$name) {
    $request = @{
        assetType = "Animation"
        displayName = $name
        description = "Maximum Pain animation: $name"
        creationContext = @{ creator = @{ userId = $UserId } }
    } | ConvertTo-Json -Depth 5 -Compress
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        $form = New-Object System.Net.Http.MultipartFormDataContent
        $form.Add((New-Object System.Net.Http.StringContent($request, [System.Text.Encoding]::UTF8, "application/json")), "request")
        $file = New-Object System.Net.Http.ByteArrayContent(, [System.IO.File]::ReadAllBytes((Join-Path $OutDir "$name.rbxmx")))
        $file.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("model/x-rbxm")
        $form.Add($file, "fileContent", "$name.rbxmx")
        $response = $client.PostAsync("https://apis.roblox.com/assets/v1/assets", $form).Result
        $body = $response.Content.ReadAsStringAsync().Result
        if ([int]$response.StatusCode -eq 429 -or [int]$response.StatusCode -ge 500) {
            Write-Host "  $([int]$response.StatusCode), waiting $(5 * $attempt) s"
            Start-Sleep -Seconds (5 * $attempt)
            continue
        }
        if (-not $response.IsSuccessStatusCode) { throw "upload of $name failed: $([int]$response.StatusCode) $body" }
        $operation = $body | ConvertFrom-Json
        for ($poll = 0; $poll -lt 60; $poll++) {
            if ($operation.done) {
                if ($operation.error) { throw "upload of $name failed: $($operation.error | ConvertTo-Json -Compress)" }
                return [string]$operation.response.assetId
            }
            Start-Sleep -Seconds 1
            $id = if ($operation.operationId) { $operation.operationId } else { ($operation.path -split "/")[-1] }
            $operation = $client.GetAsync("https://apis.roblox.com/assets/v1/operations/$id").Result.Content.ReadAsStringAsync().Result | ConvertFrom-Json
        }
        throw "upload of $name didn't finish in 60 s (operation $($operation.path))"
    }
    throw "upload of $name kept being refused"
}

if (-not ($Build -or $Upload)) { throw "Pass -Build, -Upload, or both." }

if ($Build) {
    New-Item -ItemType Directory -Force $OutDir | Out-Null
    $clips = Get-Content (Join-Path $Exports "keyframes.json") -Raw | ConvertFrom-Json
    $count = 0
    foreach ($clip in $clips) {
        if ($Only -and $Only -notcontains $clip.name) { continue }
        Write-Clip $clip
        $count++
    }
    Write-Host "Built $count clip files in $OutDir"
}

if ($Upload) {
    if (-not $env:ROBLOX_API_KEY) { throw "Set ROBLOX_API_KEY to an Open Cloud key made on 83tg first." }
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Add-Type -AssemblyName System.Net.Http
    $client = New-Object System.Net.Http.HttpClient
    $client.DefaultRequestHeaders.Add("x-api-key", $env:ROBLOX_API_KEY.Trim().Trim('"', "'"))
    $ids = Load-Ids
    $names = Get-ChildItem $OutDir -Filter *.rbxmx | ForEach-Object { $_.BaseName } | Sort-Object
    if ($Only) { $names = $names | Where-Object { $Only -contains $_ } }
    $done = 0
    foreach ($name in $names) {
        if ($ids.Contains($name) -and -not $Force) { continue }
        Write-Host "Uploading $name"
        $ids[$name] = Send-Clip $client $name
        Save-Ids $ids
        Write-Host "  $name -> $($ids[$name])"
        $done++
        Start-Sleep -Milliseconds 500
    }
    Write-Host "Uploaded $done clips; $($ids.Count) ids in $IdsFile"
}
