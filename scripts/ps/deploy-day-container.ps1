az container delete --resource-group fxcm-trader --name day-trader
az container create --resource-group fxcm-trader --name day-trader --file ../containers/day-container.yaml
pause