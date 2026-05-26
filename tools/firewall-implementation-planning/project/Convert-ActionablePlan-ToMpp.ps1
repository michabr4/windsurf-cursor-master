#Requires -Version 5.1
<#
  Converts the generated MS Project XML to a native .mpp (requires Microsoft Project for Windows / Office).

  Usage (PowerShell, on a PC with Project installed):
    cd <path-to-repo>\project
    .\Convert-ActionablePlan-ToMpp.ps1

  This script uses the Project COM object. It may require Project desktop 2016+ / Microsoft 365 Apps with Project.
#>

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$xml = Join-Path $here 'MGM_Palo_to_Cisco_Actionable_Plan.xml'
$mpp = Join-Path $here 'MGM_Palo_to_Cisco_Actionable_Plan.mpp'

if (-not (Test-Path -LiteralPath $xml)) {
  Write-Error "Missing XML: $xml"
  exit 1
}

# pjMPP = 10  (https://docs.microsoft.com/office/vba/api/Project.PjFileFormat)
$pjMPP = 10

try {
  $proj = New-Object -ComObject MSProject.Application
  $proj.Visible = $true
} catch {
  Write-Error "Could not start Microsoft Project. Is Project for Windows installed? $_"
  exit 1
}

try {
  $proj.FileOpen($xml, [Type]::Missing, [Type]::Missing, $false, [Type]::Missing, [Type]::Missing, $true)
  if (Test-Path -LiteralPath $mpp) { Remove-Item -LiteralPath $mpp -Force }
  $proj.FileSaveAs($mpp, $pjMPP)
  Write-Host "Saved: $mpp"
} finally {
  $proj.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($proj) | Out-Null
}
