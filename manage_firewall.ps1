$RuleName = "POS Printer Server (8000, 9100)"
$Ports = "8000,9100"

function Check-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "--------------------------------------------------------" -ForegroundColor Red
        Write-Host "ERROR: DEBES EJECUTAR ESTE SCRIPT COMO ADMINISTRADOR." -ForegroundColor Red
        Write-Host "Haz clic derecho sobre el archivo y selecciona 'Ejecutar con PowerShell'." -ForegroundColor Yellow
        Write-Host "--------------------------------------------------------" -ForegroundColor Red
        Pause
        exit
    }
}

if ($args.Count -eq 0) {
    Write-Host "Uso: .\manage_firewall.ps1 -Action [enable|disable]" -ForegroundColor Cyan
    Write-Host "Ejemplo: .\manage_firewall.ps1 enable"
    exit
}

$Action = $args[0]
Check-Admin

if ($Action -eq "enable") {
    Write-Host "Habilitando acceso externo para los puertos $Ports..." -ForegroundColor Cyan
    # Eliminar regla antigua si existe para evitar duplicados
    netsh advfirewall firewall delete rule name=$RuleName > $null
    # Crear la nueva regla
    netsh advfirewall firewall add rule name=$RuleName dir=in action=allow protocol=TCP localport=$Ports
    Write-Host "[OK] Regla de Firewall creada correctamente." -ForegroundColor Green
    Write-Host "Ahora puedes acceder desde otros dispositivos usando tu IP local." -ForegroundColor White
}
elseif ($Action -eq "disable") {
    Write-Host "Eliminando regla de firewall..." -ForegroundColor Cyan
    netsh advfirewall firewall delete rule name=$RuleName
    Write-Host "[OK] Regla eliminada. El acceso externo ha sido bloqueado." -ForegroundColor Yellow
}

Pause
