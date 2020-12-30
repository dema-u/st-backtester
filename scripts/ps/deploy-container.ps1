$Currency = Read-Host -Prompt 'Input Currency'
$FileName = -join($Currency, '.yaml')
$ContainerPath = Join-Path ../containers/ $FileName

az container delete --resource-group fxcm-trader --name $Currency
az container create --resource-group fxcm-trader --name $Currency --file $ContainerPath
pause