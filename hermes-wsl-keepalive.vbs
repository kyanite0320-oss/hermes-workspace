' Hermes WSL Keepalive - Hidden launcher
' Runs the .bat script silently (no console window)
' Parameter 0 = hide window, False = don't wait for completion
CreateObject("WScript.Shell").Run "F:\AI\hermes\hermes-wsl-keepalive.bat", 0, False
