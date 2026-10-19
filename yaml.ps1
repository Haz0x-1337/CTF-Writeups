# --------------------------------------------------------------------
# Fixed script – adds YAML front‑matter to every *.md file that contains
# a “lab:” line.
# --------------------------------------------------------------------
$targetFolder = "C:\Users\Zephyr\Documents\Github\CTF-Writeups\"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

# Get all markdown files recursively
$files = Get-ChildItem -Path $targetFolder -Filter "*.md" -Recurse

foreach ($file in $files) {
    # Read the file’s lines
    $lines = Get-Content $file.FullName

    # Prepare a collection for the new lines we’ll add
    $newLines = @()

    # Variables that track the current lab name and whether we need to update
    $dashCount = 0
    $labName   = "machine"
    $needsUpdate = $false

    foreach ($line in $lines) {

        # -----------------------------------------------------------------
        # Detect a “lab:” line, rename it to “title:” and remember the name
        # -----------------------------------------------------------------
        if ($line -match '^lab:\s*"?([^"]*)"?') {
            $labName   = $matches[1]
            $line      = $line -replace '^lab:', 'title:'
            $needsUpdate = $true
        }

        # -----------------------------------------------------------------
        # When we hit the second "---" we inject our new front‑matter
        # -----------------------------------------------------------------
        if ($line -match '^---$') {
            $dashCount++

            if ($dashCount -eq 2 -and $needsUpdate) {
                # Avoid adding the draft twice if the script runs again
                $alreadyHasDraft = ($lines -match '^draft:').Count -gt 0

                if (-not $alreadyHasDraft) {
                    $newLines += 'tags: ["writeup"]'
                    $newLines += "summary: Writeup for the $labName machine."
                    $newLines += 'draft: false'
                }
            }
        }

        # Keep the original line (or the modified one) in the output array
        $newLines += $line
    }

    # If we made any changes, write the updated content back to the file
    if ($needsUpdate) {
        [System.IO.File]::WriteAllLines($file.FullName, $newLines, $utf8NoBom)
        Write-Host "Updated: $($file.FullName)" -ForegroundColor Green
    }
}