Fichier systemd
sudo nano /etc/systemd/system/video-player.service
copier le contenue de service.ini
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable video-player
sudo systemctl start video-player
sudo systemctl status video-player
sudo systemctl stop video-player
sudo systemctl disable video-player
sudo systemctl restart video-player
journalctl -u video-player -f
