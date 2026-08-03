$ErrorActionPreference='Continue'
$editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$proj='C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject'
$dir='C:\Users\edwar\project-uppercut\sandbox\Saved\BPTick'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$results=@()
foreach ($tag in @($args[0], $args[1])) {
  if (-not $tag) { continue }
  $logDir='C:\Users\edwar\project-uppercut\sandbox\Saved\Logs'
  Get-ChildItem $logDir -Filter 'UppercutSandbox.log' | Remove-Item -Force -ErrorAction SilentlyContinue
  $a=@($proj,'L_DeterminismProbe','-game','-UseFixedTimeStep','-FPS=60','-unattended','-nopause','-nosplash','-log')
  $p=Start-Process -FilePath $editor -ArgumentList $a -PassThru -WindowStyle Hidden
  $deadline=(Get-Date).AddMinutes(9)
  while (-not $p.HasExited) {
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" | Where-Object { $_.CommandLine -match 'Build\.bat.+ValidatePlatforms' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Milliseconds 900
    if ((Get-Date) -gt $deadline) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; break }
  }
  Start-Sleep -Seconds 3
  $src=Join-Path $logDir 'UppercutSandbox.log'
  $out=Join-Path $dir "$tag.txt"
  if (Test-Path $src) {
    $m = Select-String -Path $src -Pattern '(P\|[\d\|\-]+)\s*$' -AllMatches | ForEach-Object { $_.Matches[0].Groups[1].Value }
    if ($m -and $m.Count -gt 0) {
      [IO.File]::WriteAllText($out, (($m -join "`n") + "`n"), [Text.UTF8Encoding]::new($false))
      $results += "$tag markers=$($m.Count) sha=$((Get-FileHash $out -Algorithm SHA256).Hash)"
    } else { $results += "$tag NO_MARKERS exit=$($p.ExitCode)" }
    Copy-Item $src (Join-Path $dir "$tag.runlog") -Force
  } else { $results += "$tag NO_LOG" }
}
[IO.File]::WriteAllText((Join-Path $dir 'summary.txt'), (($results -join "`n") + "`n"), [Text.UTF8Encoding]::new($false))