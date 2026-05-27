@echo off
schtasks /CREATE /SC ONLOGON /TN HermesSoulPull /TR "wsl.exe -u administrator bash /home/administrator/.hermes/scripts/soul-pull.sh" /RL LIMITED /F
echo Done.
