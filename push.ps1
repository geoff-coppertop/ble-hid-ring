# script to deploy CircuitPython code to devboard

param (
    [ValidateScript({if ($_){ Test-Path $_}})]
    [Parameter(Mandatory,
    HelpMessage="Enter the target folder.")]
    [string] $targetFolder
)

# use the current directory as the source folder
$sourceItemFolder="$PSScriptRoot"

# array of files to deploy
$includedFiles = Get-Content -Path .\included_files.txt -ErrorAction SilentlyContinue
if (!$?) {
    Write-Output $_
    Write-Output "-- Warning --"
    Write-Output "included_files.txt not found."
    Write-Output "Not copying any files..."
    $includedFiles = [System.Collections.ArrayList]::new()
}

# Copy the files
ForEach ( $file in $includedFiles ) {
    $fileSourcePath = Join-Path $sourceItemFolder $file
    $fileTargetPath = Join-Path $targetFolder $file
    $fileTargetFolder = Split-Path -Parent $fileTargetPath
    New-Item -ItemType Directory -Path $fileTargetFolder -ErrorAction SilentlyContinue
    Copy-Item $fileSourcePath $fileTargetPath
}

# install dependencies to devboard
circup install -r requirements_cp.txt
