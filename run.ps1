# Shortcuts to run WeatherBot locally (PowerShell)
param(
    [string]$cmd = "help"
)

if ($cmd -eq "help") {
    Write-Output "Usage: .\run.ps1 [train|run|actions|shell]"
    exit 0
}

if ($cmd -eq "train") {
    rasa train
}
elseif ($cmd -eq "actions") {
    python -m rasa_sdk.endpoint --actions actions
}
elseif ($cmd -eq "run") {
    Start-Process "rasa" -ArgumentList "run" -NoNewWindow
    Start-Process "powershell" -ArgumentList "-NoExit -Command python -m rasa_sdk.endpoint --actions actions" -NoNewWindow
}
elseif ($cmd -eq "shell") {
    rasa shell
}
else {
    Write-Output "Unknown command"
}
