# fix-image-paths.ps1
# Run this from the root of your CTF-Writeups repository.
# Rewrites ![](Labs/Attachments/...) to ![](../Attachments/...) in all .md files.

$root = Get-Location
$old = '![](Labs/Attachments/'
$new = '![](../Attachments/'

$files = Get-ChildItem -Path $root -Recurse -Filter '*.md' -File |
    Where-Object { $_.FullName -notmatch '\\\.git\\' }

$changed = @()

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName)

    if ($content.Contains($old)) {
        $updated = $content.Replace($old, $new)
        [System.IO.File]::WriteAllText($file.FullName, $updated)
        $changed += $file.FullName
        Write-Host "Fixed: $($file.FullName.Substring($root.Path.Length + 1))"
    }
}

Write-Host ""
Write-Host "Done. $($changed.Count) file(s) updated."
