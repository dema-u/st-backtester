az container delete --resource-group fxcm-trader --name night-trader
az container create --resource-group fxcm-trader --name night-trader --file ../containers/night-container.yaml
pause